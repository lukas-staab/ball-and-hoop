import multiprocessing
import os
import shutil

import cv2

from src.ballandhoop import WhiteBalancing, Hoop, Ball, helper, Image
import socket
import yaml
import scipy.io

from src.network import init_network
from src.ballandhoop.videostream import VideoStream


class Application:
    """loads config, starts network, starts tracking"""

    def __init__(self, force_hostname=None, verbose_output=False):
        self.verbose = verbose_output
        self.cfg = self.load_config_from_disk('yml')
        if force_hostname is None:
            self.hostname = socket.gethostname()
        else:
            self.print('[INFO] Forcing different hostname: ' + force_hostname)
            self.hostname = force_hostname
        self.network = None

        # if debug folder exists, delete it (and its contents) and re-create a new one
        if os.path.isdir('storage/debug/'):
            shutil.rmtree('storage/debug/')
        os.makedirs('storage/debug/')

    def load_config_from_disk(self, file_type='yml'):
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
        return self.cfg[self.hostname]

    def get_cfg(self, *arg):
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
        self.print("Try to update config files - if this fails, remove keys with empty values from source config")
        self.print(self.cfg)
        with open('config.yml', 'w') as outfile:
            yaml.dump(self.cfg, outfile, default_flow_style=None)
        scipy.io.savemat('config.mat', {'pi_configs': self.cfg})
        self.print('Updated config file(s)')

    def run_calibration(self, calc_wb_gains: bool,
                        search_hoop: bool, hoop_search_col: dict,
                        search_ball: bool, ball_search_col: dict):
        helper.reset_content_of_dir('storage/calibration/')
        self.print('=== Start Calibration')
        if calc_wb_gains:
            self.print('|-> Start White Balancing Calibration')
            self.local_config()['video']['wb_gains'] = WhiteBalancing(verboseOutput=False).calculate(cropping=True)
        self.print('|-> Using white balancing Gains: ' + str(self.get_cfg('video', 'wb_gains')))
        if search_hoop:
            self.print('|-> Searching Hoop in new picture')
            hoop_search_col = self.save_col_and_add_from_config('hoop', hoop_search_col)
            hoop, im = Hoop.create_from_image(**hoop_search_col, pic=self.get_cfg('hoop', 'faker_path'),
                                              iterations=0, debug_output_path='storage/calibration/')
            if hoop is not None:
                self.local_config()['hoop']['radius'] = hoop.radius
                self.local_config()['hoop']['center'] = hoop.center
                self.local_config()['hoop']['center_dots'] = hoop.center_dots
                self.local_config()['hoop']['radius_dots'] = hoop.radius_dots
                self.print('|-> Hoop found @ ' + str(self.get_cfg('hoop', 'center')))
            else:
                self.print('|-> NO HOOP FOUND! - see in storage/calibration/ for debug pictures')
        self.print('|-> Using Hoop @ ' + str(self.get_cfg('hoop', 'center')) + " with r=" +
                   str(self.get_cfg('hoop', 'radius')))
        if search_ball and self.get_cfg('hoop', 'center') is not None:
            self.print('|-> searching for ball / Testing color')
            ball_search_col = self.save_col_and_add_from_config('ball', ball_search_col)
            hoop = Hoop(**self.get_cfg('hoop'))
            pic = helper.get_hsv_picture(self.get_cfg('hoop', 'faker_path'))
            ball = hoop.find_ball(frame=pic, cols=ball_search_col, iterations=1)
            im = Image(image_hsv=pic)
            if ball is not None:
                self.print("|-> Ball found @ " + str(ball.center) + " with r=" + str(ball.radius))
                im = im.plot_ball(ball)
            else:
                self.print("|-> NO BALL FOUND!")
            self.print('Save debug images to storage/calibration/')
            cv2.imwrite('storage/calibration/ball-hsv.png', im.image_hsv)
            cv2.imwrite('storage/calibration/ball-rgb.png', im.image_bgr)
        self.print('=== End Calibration')
        self.save_config_to_disk()

    def run(self, ball_search_col: dict):
        # give config to object constructors to initialize like defined in config
        # ** does flatten the array to arguments, with their corresponding keys as argument names
        hoop = Hoop(**self.get_cfg('hoop'))
        video = VideoStream(**self.get_cfg('video'))
        # the network needs object context for better access in the async callback method from the workers
        self.network = init_network(**self.get_cfg('network'))
        # get ball color from console parameters and save the new one to config - if not given get values from config
        ball_search_col = self.save_col_and_add_from_config('ball', ball_search_col)
        try:
            # start network
            with self.network:
                # start thread-worker pool,
                with multiprocessing.Pool(processes=os.cpu_count()) as pool:
                    # count the number of frames, this might be important to reconstruct original frame order
                    i = 0
                    # iterate over the video frames
                    for frame in video:
                        # increase frame counter
                        i = i + 1
                        # send the task to the next available thread-worker, from the pool
                        # the threads will call hoop.find_ball(frame=frame, cols=ball_search_col, iterations=0)
                        # search for the ball in the frame with the given color borders
                        pool.apply_async(hoop.find_ball,
                                         args=(frame, ball_search_col, 0),
                                         callback=self.network_async_callback)
                        # TODO?: callback for errors in apply_async - right now it fails silent
                        # if in debuging mode save every 30th frame for debugging purposes
                        if self.verbose and i % 30 == 0:
                            cv2.imwrite('./storage/debug/' + str(i) + "-hsv.png", frame)
                            # cv2 expects bgr format as default
                            cv2.imwrite('./storage/debug/' + str(i) + "-rgb.png", cv2.cvtColor(frame, cv2.COLOR_HSV2BGR))

        except KeyboardInterrupt:
            # break potential infinite loop
            pass
        finally:
            video.close()

    def network_async_callback(self, ball: Ball):
        # send the ball angle result to the network
        if ball is not None:
            self.network.send(ball.angle_in_hoop())
        else:
            print('No ball found')

    def print(self, msg: str):
        if self.verbose:
            print(msg)

    def save_col_and_add_from_config(self, type: str, input: dict):
        ret = {}
        if input['lower'] is not None:
            self.local_config()[type]['hsv']['lower'] = input['lower']
        ret['lower'] = self.get_cfg(type, 'hsv', 'lower')
        if input['upper'] is not None:
            self.local_config()[type]['hsv']['upper'] = input['upper']
        ret['upper'] = self.get_cfg(type, 'hsv', 'upper')
        self.save_config_to_disk()
        return ret

    def debug(self, save_vid=None, wb_gains=None):
        if wb_gains is None:
            wb_gains = WhiteBalancing(verboseOutput=False).calculate(cropping=True)
            self.print('Calced wb_gains: ' + str(wb_gains))

        if save_vid is not None:
            from src.faker.save import savePictures
            # the * does flatten the array to arguments, without key as name
            savePictures(*save_vid, wb_gains=wb_gains)
            self.print('Saved Picture')
