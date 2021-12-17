import hashlib
import json
import logging
import time

import brotli
import yaml

from foe_bot.exceptions import RequestException
from foe_bot.login import Login
from foe_bot.util import foe_json_loads


class Request(object):
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not Request.__shared_state:
            self.__logger = logging.getLogger("Request")
            self.__wait_between_req = 0.5
            cfg = self.__load_config()
            self._session, self._initial_response = Login(cfg[0]['lang'], cfg[0]['world']).login(cfg[0]['username'],
                                                                                                 cfg[0]['password'])

    def send(self, body: str):
        signature = self.__sign(body, self._session.cookies.get('clientId'), self._session.cookies.get('signature_key'))
        query = {'h': self._session.cookies.get('clientId')}
        header = {'Signature': signature}

        response = self._session.post('https://de14.forgeofempires.com/game/json', data=body, params=query,
                                      headers=header)
        if not (response.status_code == 200):
            raise RequestException("Did not get a 200 response code: %s" % response.content)

        content = response.content.decode()

        if 'error' in content:
            self.__logger.error(f"request failed > request:'{body}', response:'{content}'")

        time.sleep(self.__wait_between_req)
        return foe_json_loads(content)

    def create_rest_body(self, klass, method, data) -> str:
        request_id = self.__get_and_increment_request_id()
        raw_body = [{
            'requestClass': klass,
            'requestData': data,
            'requestId': request_id,
            'requestMethod': method,
            '__class__': "ServerRequest"
        }]
        return json.dumps(raw_body, separators=(',', ':'))

    def create_ws_body(self, klass, method, data) -> str:
        request_id = self.__get_and_increment_request_id()
        raw_body = {
            'requestClass': klass,
            'requestData': data,
            'requestId': request_id,
            'requestMethod': method,
            '__class__': "ServerRequest"
        }
        return json.dumps(raw_body, separators=(',', ':'))

    def __get_and_increment_request_id(self):
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

    @property
    def headers(self):
        return self._session.headers
