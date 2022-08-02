import yaml


class Application:
    """loads config, starts network, starts tracking"""

    def __init__(self):
        with open("./config.yml", "r") as ymlfile:
            self.cfg = yaml.load(ymlfile, Loader=yaml.Loader)
            print(self.cfg)
        for val in self.cfg:
            print(val)


if __name__ == '__main__':
    Application()
