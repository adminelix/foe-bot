import logging.config
import os
import sys

import yaml

config_file = f"{os.path.dirname(os.path.realpath(__file__))}/../config.yml"


def load_config():
    with open(config_file, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


cfg = load_config()

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
                    stream=sys.stdout)
logging.getLogger("seleniumwire.handler").setLevel(logging.WARN)
logging.getLogger("seleniumwire.server").setLevel(logging.WARN)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)
