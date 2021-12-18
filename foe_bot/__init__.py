import logging
import sys

import yaml


def load_config():
    with open("../config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


cfg = load_config()

Log_Format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    format=Log_Format,
    level=logging.INFO)
