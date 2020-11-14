import requests
import yaml
from login import Login
import time


def loadConfig():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


def prepareRequest():
    r = requests.Session()
    for cookie in cookies:
        r.cookies.set(cookie['name'], cookie['value'])


cfg = loadConfig()
cookies = Login(cfg[0]['lang'], cfg[0]['world']).login(
    cfg[0]['username'], cfg[0]['password'])
time.sleep(30)
prepareRequest()
