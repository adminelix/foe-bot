import logging.config

import yaml


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


cfg = load_config()

logging.config.fileConfig('logging.conf')
logging.getLogger("seleniumwire.handler").setLevel(logging.WARN)
logging.getLogger("seleniumwire.server").setLevel(logging.WARN)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)
