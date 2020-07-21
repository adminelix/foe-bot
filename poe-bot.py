import requests
import yaml
from login import Login


def loadConfig():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


cfg = loadConfig()
cookie = Login(cfg[0]['lang']).login(cfg[0]['username'], cfg[0]['password'])


# def foo():
#     r = requests.Session()
