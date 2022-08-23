import random
import time
from os.path import abspath, join, dirname
from src.ballandhoop import WhiteBalancing, Hoop
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
            yaml.dump(self.cfg, outfile, default_flow_style=False)
        scipy.io.savemat('config.mat', {'pi_configs': self.cfg})
        self.print('Updated config file(s)')

    def run_calibration(self, calc_wb_gains: bool, search_hoop: bool, hoop_search_col: dict):
        self.print('=== Start Calibration')
        if calc_wb_gains:
            self.print('|-> Start White Balancing Calibration')
            self.local_config()['video']['wb_gains'] = WhiteBalancing(verboseOutput=False).calculate(cropping=True)
        self.print('|-> Using white balancing Gains: ' + str(self.get_cfg('wb_gains')))
        if search_hoop:
            self.print('|-> Searching Hoop in new picture')
            hoop_search_col = self.save_col_and_add_from_config('hoop', hoop_search_col)
            hoop = Hoop.create_from_image(**hoop_search_col)
            if hoop is not None:
                hoop_cfg = {
                    'radius': hoop.radius,
                    'center': hoop.center,
                    'center_dots': hoop.center_dots,
                    'radius_dots': hoop.radius_dots,
                }
                self.local_config()['hoop'] = hoop_cfg
                self.print('|-> Hoop found @ ' + str(self.get_cfg('hoop', 'center')))
            else:
                self.print('|-> NO HOOP FOUND! - see in storage/hoop/ for debug pictures')
        self.print('|-> Using Hoop @ ' + str(self.get_cfg('hoop', 'center')) + " with r=" + str(
            self.get_cfg('hoop', 'radius')))
        self.print('=== End Calibration')

    def run(self, ball_search_col: dict):
        # give config to objects to initialize
        hoop = Hoop(**self.get_cfg('hoop'))
        video = VideoStream(**self.get_cfg('video'))
        network = init_network(**self.get_cfg('network'))

        ball_search_col = self.save_col_and_add_from_config('ball', ball_search_col)
        try:
            with network:
                for f in video:
                    # do the tracking and send the result here to the network
                    ball = hoop.find_ball(frame=f, cols=ball_search_col)
                    # send the result
                    if ball is not None:
                        network.send(ball.angle_in_hoop())
                    else:
                        network.send('None')
        except KeyboardInterrupt:
            # break potential infinite loop
            pass
        finally:
            video.close()

    def print(self, msg: str):
        if self.verbose:
            print(msg)

    def save_col_and_add_from_config(self, type: str, input: dict):
        ret = {}
        if input['lower'] is not None:
            self.get_cfg()[type]['hsv']['lower'] = input['lower']
        ret['lower'] = self.get_cfg()[type]['hsv']['lower']
        if input['upper'] is not None:
            self.get_cfg()[type]['hsv']['upper'] = input['upper']
        ret['upper'] = self.get_cfg()[type]['hsv']['upper']
        return ret

    def debug(self, save_vid=None, wb_gains = None):
        if wb_gains is None:
            wb_gains = WhiteBalancing(verboseOutput=False).calculate(cropping=True)
            self.print('Calced wb_gains: ' + str(wb_gains))

        if save_vid is not None:
            from src.faker.save import savePictures
            savePictures(* save_vid, wb_gains=wb_gains)
            self.print('Saved Picture')
