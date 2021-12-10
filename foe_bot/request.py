import hashlib
import json

import brotli
import yaml

from foe_bot.login import Login


class Request(object):
    __shared_state = {}

    def __init__(self):
        if not Request.__shared_state:
            self.__dict__ = self.__shared_state
            cfg = self.__load_config()
            self._session, self._initial_response = Login(cfg[0]['lang'], cfg[0]['world']).login(cfg[0]['username'],
                                                                                                 cfg[0]['password'])

    def send(self, klass: str, method: str, data):
        request_id = self.get_and_increment_request_id()
        raw_body = [{
            'requestClass': klass,
            'requestData': data,
            'requestId': request_id,
            'requestMethod': method,
            '__class__': "ServerRequest"
        }]

        body = json.dumps(raw_body, separators=(',', ':'))

        signature = self.__sign(body, self._session.cookies.get('clientId'), self._session.cookies.get('signature_key'))
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

    def get_and_increment_request_id(self):
        request_id = self._session.cookies['request_id'] + 1
        self._session.cookies.set('request_id', request_id, path='/', domain='local')
        return request_id

    @staticmethod
    def __load_config():
        with open("../config.yml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
            return cfg

    @staticmethod
    def __sign(body, client_id, signature_key):
        id_ = client_id + signature_key + body
        return hashlib.md5(id_.encode()).hexdigest()[1:11]

    @property
    def initial_response(self):
        return self._initial_response