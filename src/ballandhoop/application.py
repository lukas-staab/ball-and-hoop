import os
from os.path import abspath, join, dirname
from src.ballandhoop import WhiteBalancing, Hoop
import socket
import yaml
import scipy.io


class Application:
    """loads config, starts network, starts tracking"""

    fallback_hostname = 'rpi1'

    def __init__(self):
        self.cfg = self.load_config_from_disk('yml')
        self.hostname = socket.gethostname()
        if self.get_cfg('all', 'run_calibration', 'next_run') or self.get_cfg('all', 'run_calibration', 'every_run'):
            self.run_calibration()
        self.hoop = Hoop(** self.get_cfg('hoop'))
        self.save_config_to_disk()

    def load_config_from_disk(self, file_type='yml'):
        cfg = None
        if file_type == 'yml':
            with open('config.yml') as cfgFile:
                cfg = yaml.load(cfgFile, Loader=yaml.Loader)
        elif file_type == 'mat':
            cfg = scipy.io.loadmat('config.mat')['pi_configs']
        print('=== Start Config ===')
        print(cfg)
        print('=== End Config ===')
        return cfg

    def local_config(self, fallback_hostname='rpi1'):
        if self.hostname not in self.cfg:
            print('[WARN] Hostname not found - assuming you are on rpi1')
            self.hostname = Application.fallback_hostname
        return self.cfg[self.hostname]

    def get_cfg(self, *arg):
        if arg[0] != 'all':
            cfg = self.cfg
        else:
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
        print("Try to update config files - if this fails, remove keys with empty values from source config")
        print(self.cfg)
        with open('config.yml', 'w') as outfile:
            yaml.dump(self.cfg, outfile, default_flow_style=False)
        scipy.io.savemat('config.mat', {'pi_configs': self.cfg})
        print('Updated config file(s)')

    def run_calibration(self):
        print('Start Calibration')
        self.cfg['all']['run_calibration']['next_run'] = False
        print('|-> Start White Balancing Calibration')
        self.local_config()['wb_gains'] = WhiteBalancing(verboseOutput=False).calculate()
        print('|-> Searching Hoop in new picture')
        lower_hsv = self.get_cfg('all', 'hsv', 'hoop', 'lower')
        upper_hsv = self.get_cfg('all', 'hsv', 'hoop', 'upper')
        hoop = Hoop.create_from_image(lower_hsv=lower_hsv, upper_hsv=upper_hsv)
        hoop_cfg = {
            'radius': hoop.radius,
            'center': hoop.center,
            'center_dots': hoop.center_dots,
            'radius_dots': hoop.radius_dots,
        }
        self.get_cfg()['hoop'] = hoop_cfg


if __name__ == '__main__':
    os.chdir(abspath(dirname(dirname(dirname(__file__)))))
    Application()
