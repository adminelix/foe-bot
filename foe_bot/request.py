import hashlib

import brotli
import yaml

from foe_bot.login import Login


class Request(object):
    __shared_state = {}

    def __init__(self):
        if not Request.__shared_state:
            self.__dict__ = self.__shared_state
            cfg = self.__load_config()
            self._session, contents = Login(cfg[0]['lang'], cfg[0]['world']).login(cfg[0]['username'],
                                                                                   cfg[0]['password'])

    def send(self, body):
        signature = self.__sign(body, self._session.cookies.get('clientId'))
        query = {'h': self._session.cookies.get('clientId')}
        header = {'Signature': signature}

        response = self._session.post('https://de14.forgeofempires.com/game/json', data=body, params=query,
                                      headers=header)
        if not (response.status_code == 200):
            raise Exception("Did not get a 200 response code: %s" % response.content)

        try:
            content = response.json()
        except Exception:
            content = brotli.decompress(response.content)

        return content

    @staticmethod
    def __load_config():
        with open("../config.yml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
            return cfg

    @staticmethod
    def __sign(body, client_id):
        key = 'd3SyKkX7UZIjCms7LelK/UrOIrEZsLv+Z1DGNTAKbWqm3aTrAkyxMYR2P3IDmYchr3LRchFpsEF0T1kykaBCpg=='
        id_ = client_id + key + body
        return hashlib.md5(id_.encode()).hexdigest()[1:11]
