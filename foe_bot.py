import requests
import yaml
from login import Login
import time


def main():
    cfg = load_config()
    cookies = Login(cfg[0]['lang'], cfg[0]['world']).login(
        cfg[0]['username'], cfg[0]['password'])
    time.sleep(30)
    prepare_request(cookies)


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
        return cfg


def prepare_request(cookies):
    r = requests.Session()
    for cookie in cookies:
        r.cookies.set(cookie['name'], cookie['value'])


if __name__ == "__main__":
    main()
