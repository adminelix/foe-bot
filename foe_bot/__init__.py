import logging.config
import os

import yaml

config_file = f"{os.path.dirname(os.path.realpath(__file__))}/../config.yml"
logging_file = f"{os.path.dirname(os.path.realpath(__file__))}/../logging.conf"


def load_config():
    with open(config_file, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


cfg = load_config()

logging.config.fileConfig(logging_file)
logging.getLogger("seleniumwire.handler").setLevel(logging.WARN)
logging.getLogger("seleniumwire.server").setLevel(logging.WARN)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)
