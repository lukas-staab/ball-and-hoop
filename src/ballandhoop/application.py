import multiprocessing
import os
import shutil
import socket
import time
import traceback

import scipy.io
import yaml

from src.ballandhoop import WhiteBalancing, Hoop, helper, Image
from src.ballandhoop.videostream import VideoStream
from src.network import init_network


class Application:
    """
    The main class to run the software. loads and saves config, loads resources with config parameters.
    This class is called out of runner.py and calibration.py with different methods.

    :param force_hostname: if unset socket.gethostname() will be used to search the for the config
    :type force_hostname: str, optional, default=None
    :param verbose_output: optional argument, if True there will be (more) output to the console, none if False
    :type verbose_output: bool, optional, default=False

    :ivar cfg: the config loaded and saved to `config.yml` (saved also to `config.mat`)
    :ivar hostname: the local hostname by either `socket.gethostname() or `force_hostname`
    :ivar network: either the server or client instance, using the :py:class:`.NetworkInterface`
    :ivar timings: a fifo dict, which saved the in time of the frame, old entries are removed after the frame calc
    :ivar latest_frame_number: remembers which is the newest frame with a result to discard older results
    :ivar result_lock: manages the thread safe access to the :py:attr:`latest_frame_number`
    :type result_lock: multiprocessing.Lock()
    """

    def __init__(self, force_hostname: str = None, verbose_output: bool = False):
        """
        Constructor Method, see class for signature
        """
        self.verbose = verbose_output
        self.cfg = self.load_config_from_disk('yml')
        if force_hostname is None:
            self.hostname = socket.gethostname()
        else:
            self.print('[INFO] Forcing different hostname: ' + force_hostname)
            self.hostname = force_hostname
        self.network = None
        self.timings = dict()
        self.latest_frame_number = 0
        self.result_lock = multiprocessing.Lock()
        # if debug folder exists, delete it (and its contents) and re-create a new one
        if os.path.isdir('storage/debug/'):
            shutil.rmtree('storage/debug/')
        os.makedirs('storage/debug/')

    def load_config_from_disk(self, file_type: str = 'yml'):
        """
        Loads the config file from the disk to the attribute

        :param file_type: the file type of the config file, can either be 'yml' or 'mat'
        :type file_type: str, optional, default='yml'
        :return: dictionary of the config content
        """
        cfg = None
        if file_type == 'yml':
            with open('config.yml') as cfgFile:
                cfg = yaml.load(cfgFile, Loader=yaml.Loader)
        elif file_type == 'mat':
            cfg = scipy.io.loadmat('config.mat')['pi_configs']
        self.print('=== Start Config ===')
        self.print(cfg)
        self.print('=== End Config ===')
        return cfg

    def local_config(self):
        """
        Wrapper Method to get the config for this hostname. The hostname might be forged in the constructor.
        Do not call this method for getting the config, just for setting it. Use :method `get_cfg`  instead

        :return: dictionary of the local config
        """
        return self.cfg[self.hostname]

    def get_cfg(self, *arg):
        """
        Helper method to get

        :param arg: there can be unlimited amount of arguments
        :type arg: str[]
        """
        cfg = self.local_config()
        for key in arg:
            try:
                cfg = cfg[key]
            except TypeError:
                return None
            except KeyError:
                return None
        return cfg

    def save_config_to_disk(self) -> None:
        """
        Saves the self.cfg back to config.yml and config.mat files.
        """
        self.print("Try to update config files - if this fails, remove keys with empty values from source config")
        self.print(self.cfg)
        with open('config.yml', 'w') as outfile:
            yaml.dump(self.cfg, outfile, default_flow_style=None)
        scipy.io.savemat('config.mat', {'pi_configs': self.cfg})
        self.print('Updated config file(s)')

    def run_calibration(self, calc_wb_gains: bool,
                        search_hoop: bool, hoop_hsv: dict,
                        search_ball: bool, ball_hsv: dict):
        """
        Runs the calibration method.

        :param calc_wb_gains: If this flag is set the white calibration is called
        :type calc_wb_gains: bool
        :param search_hoop: If this flag is set the hoop border points are searched
        :type search_hoop: bool
        :param hoop_hsv: a dictionary with keys `lower` and `upper`
        :type hoop_hsv: dict
        :param search_ball:
        :type search_ball: bool
        :param ball_hsv:
        :type ball_hsv: dict
        """
        helper.reset_content_of_dir('./storage/calibration/')
        self.print('=== Start Calibration')
        if calc_wb_gains:
            self.print('|-> Start White Balancing Calibration')
            self.local_config()['camera']['wb_gains'] = WhiteBalancing(verboseOutput=False).calculate(cropping=True)
        self.print('|-> Using white balancing Gains: ' + str(self.get_cfg('camera', 'wb_gains')))
        raw = Image.create(self.get_cfg('hoop', 'faker_path'), wb_gains=self.local_config()['camera']['wb_gains'])
        raw.save('./storage/calibration/', 'raw')
        if search_hoop:
            self.print('|-> Searching Hoop in new picture')
            hoop_hsv = self.save_col_and_add_from_config('hoop', hoop_hsv)

            raw.color_split('storage/calibration/hoop-colsplit-bgr', hoop_hsv['lower'],
                            hoop_hsv['upper'],
                            return_hsv=False)
            raw.color_split('storage/calibration/hoop-colsplit-hsv', hoop_hsv['lower'],
                            hoop_hsv['upper'],
                            return_hsv=True)
            hoop = Hoop.create_from_image(image=raw, debug_output_path='./storage/calibration/',
                                          **self.get_cfg('hoop'))
            if hoop is not None:
                self.local_config()['hoop']['radius'] = hoop.radius
                self.local_config()['hoop']['center'] = hoop.center
                self.local_config()['hoop']['center_dots'] = hoop.center_dots
                self.local_config()['hoop']['radius_dots'] = hoop.radius_dots
                self.print('|-> Hoop found @ ' + str(self.get_cfg('hoop', 'center')))
                raw.plot_hoop(hoop, with_dots=True).save('./storage/calibration/', 'hoop-result')
            else:
                self.print('|-> NO HOOP FOUND! - see in storage/calibration/ for debug pictures')
        self.print('|-> Using Hoop @ ' + str(self.get_cfg('hoop', 'center')) + " with r=" +
                   str(self.get_cfg('hoop', 'radius')))
        if search_ball and self.get_cfg('hoop', 'center') is not None:
            self.print('|-> searching for ball / Testing color')
            ball_hsv = self.save_col_and_add_from_config('ball', ball_hsv)
            hoop = Hoop(**self.get_cfg('hoop'))
            ball = hoop.find_ball(frame=raw.image_hsv, **self.local_config()['ball'],
                                  dir_path='storage/calibration/')
            if ball is not None:
                self.print("|-> Ball found @ " + str(ball.center) + " with r=" + str(ball.radius) +
                           " + deg=" + str(int(ball.angle())) + "°")
                raw = raw.plot_ball(ball)
            else:
                self.print("|-> NO BALL FOUND!")
            self.print('Save debug images to storage/calibration/')
            raw.color_split('storage/calibration/ball-colsplit-bgr', ball_hsv['lower'], ball_hsv['upper'],
                            return_hsv=False)
            raw.color_split('storage/calibration/ball-colsplit-hsv', ball_hsv['lower'], ball_hsv['upper'],
                            return_hsv=True)
            raw.save('storage/calibration', 'ball-result')

        self.print('=== End Calibration')
        self.save_config_to_disk()

    def run(self, ball_hsv: dict):
        """
        This method runs the main loop method for tracking and network init. Administers the thread-workers and gives
        them jobs. Each core gets one thread-worker. They will calculate the results of the frames after each other.
        The thread-workers are especially needed if the application is running under high per frame cpu,
        which can happen with high fps or high resolution settings.

        :param ball_hsv: if this parameter is set, the ball hsv in config is overwritten
        :type ball_hsv: dict
        """
        # saves the new colors to the config
        self.save_col_and_add_from_config('ball', ball_hsv)
        # give config to object constructors to initialize like defined in config
        # ** does flatten the array to arguments, with their corresponding keys as argument names
        hoop = Hoop(**self.get_cfg('hoop'))
        video = VideoStream(**self.get_cfg('camera'))
        # the network needs object context for better access in the async callback method from the workers
        self.network = init_network(**self.get_cfg('network'))
        # start network
        with self.network:
            try:
                # start thread-worker pool,
                pool = multiprocessing.Pool(processes=os.cpu_count())
                # count the number of frames, this will be important to reconstruct original frame order
                i = 0
                # iterate over the video frames (most likely infinitely)
                for frame in video:
                    # increase frame counter
                    i = i + 1
                    # log the time of frame delivery
                    self.timings[i] = time.time()

                    debug_dir_path = None
                    # if in debugging mode save every 30th frame in this folder for that frame
                    if self.verbose and i % 30 == 0:
                        debug_dir_path = './storage/debug/' + str(i) + "/"
                        os.makedirs(debug_dir_path, exist_ok=True)
                    # normal loop:
                    # send the task to the next available thread-worker, from the pool
                    # the threads will call hoop.find_ball(frame=frame, cols=ball_hsv, iterations=0)
                    # search for the ball in the frame with the given color borders
                    pool.apply_async(hoop.find_ball_async,
                                     args=(i, frame, self.local_config()['ball'], debug_dir_path),
                                     callback=self.ball_found_async_callback,
                                     error_callback=self.ball_search_error_callback)
            except KeyboardInterrupt:
                # break potential infinite loop
                pass

            finally:
                print('Closing resources, worker and so on')
                video.close()
                pool.terminate()
                pool.close()
                # pool.join()

    def ball_search_error_callback(self, e):
        """
        This is the callback method which is provided to the thread-worker. It is called if there is an error in one of
        the thread-workers. Without this method the thread-worker would fail silent.
        It still does, if verbose flag is not set

        :param e: The error
        """
        self.print('Error')
        if self.verbose:
            traceback.print_exception(type(e), e, e.__traceback__)

    def ball_found_async_callback(self, result):
        """
        The method which is called after the thread-worker run and did not fail

        :param result: the result of the thread worker, can only be one argument, the thread-worker is not able to send a second one
        :type result: tuple
        """
        # callback merges all return values in one parameter, so unmerge it
        frame_number, ball = result
        # announce that you would like to do network stuff, and reserve the resources
        with self.result_lock:
            # send the ball angle result to the network
            if frame_number <= self.latest_frame_number:
                # frame is too old, discard
                self.network.send(self.network.WRONG_ORDER)
                return
            # set new highest evaluated frame
            self.latest_frame_number = frame_number
            # send angle or error code, that no ball was found
            if ball is not None:
                self.network.send(ball.angle())
            else:
                self.network.send(self.network.NOT_FOUND)
            # remove time and calc how long whole frame took
            start_time = self.timings.pop(frame_number)
        self.print("Frame " + str(frame_number) + " took " + str(int((time.time() - start_time) * 1000)) + "ms")

    def print(self, msg: str):
        """
        Prints the message to stdout, if app is running with verbose flag, discards otherwise

        :param msg: the message string
        """
        if self.verbose:
            print(msg)

    def save_col_and_add_from_config(self, type_name: str, input_data: dict):
        """
        Saves the given parameters to config and reads config afterwards.
        If parameters are None, then only the config is read.

        :param type_name: a top level setting with a hsv child, like `ball` or `hoop`
        :param input_data: the dictionary with the `upper` and `lower` color as dict keys, with value (H,S,V)
        """
        ret = {}
        if input_data['lower'] is not None:
            self.local_config()[type_name]['hsv']['lower'] = input_data['lower']
        ret['lower'] = self.get_cfg(type_name, 'hsv', 'lower')
        if input_data['upper'] is not None:
            self.local_config()[type_name]['hsv']['upper'] = input_data['upper']
        ret['upper'] = self.get_cfg(type_name, 'hsv', 'upper')
        self.save_config_to_disk()
        return ret

    def debug(self, save_vid=None, wb_gains=None):
        """
        This method is here to generate fake video material, which can be used with the faker_path config

        :param save_vid:
        :param wb_gains: if not given, then the gains will be freshly calculated
        """
        if wb_gains is None:
            wb_gains = WhiteBalancing(verboseOutput=False).calculate(cropping=True)
            self.print('Calced wb_gains: ' + str(wb_gains))

        if save_vid is not None:
            from src.faker.save import savePictures
            # the * does flatten the array to arguments, without key as name
            savePictures(*save_vid, wb_gains=wb_gains)
            self.print('Saved Picture')
