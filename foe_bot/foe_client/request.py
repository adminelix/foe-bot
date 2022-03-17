import hashlib
import json
import logging
import re
import time
from collections import OrderedDict

import requests
from requests import Session

from foe_bot import ARGS
from foe_bot.exceptions import RequestException
from foe_bot.foe_client.login import Login
from foe_bot.util import foe_json_loads


class Request:

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__world = ARGS.world
        self.__lang = re.sub(r'[a-zA-Z]', '', ARGS.world)
        self.__wait_between_req: float = 0
        self.__session: Session
        self.initial_response: list[dict]
        self.login()

    def send(self, body: str):
        successful: bool = True
        signature = self.__sign(body, self.__session.cookies.get('clientId'),
                                self.__session.cookies.get('signature_key'))
        query = {'h': self.__session.cookies.get('clientId')}
        header = {'Signature': signature}

        try:
            response = self.__session.post(f"https://{self.__world}.forgeofempires.com/game/json", data=body,
                                           params=query, headers=header)
        except requests.exceptions.ConnectionError:
            return [], False

        if not (response.status_code == 200):
            raise RequestException("Did not get a 200 response code: %s" % response.content)

        content = response.content.decode()

        lower = content.lower()
        if 'error' in lower or 'exception' in lower:
            successful = False
            self.__logger.error(f"request failed > request:'{body}', response:'{content}'")
        if 'redirect' in lower:
            self.__logger.error(f"session expired: '{content}'")
            content = '[]'
            successful = False

        time.sleep(self.__wait_between_req)
        return foe_json_loads(content), successful

    def create_rest_body(self, klass, method, data) -> str:
        request_id = self.__get_and_increment_request_id()
        raw_body = [OrderedDict([
            ('__class__', "ServerRequest"),
            ('requestData', data),
            ('requestClass', klass),
            ('requestMethod', method),
            ('requestId', request_id)
        ])]
        return json.dumps(raw_body, separators=(',', ':'))

    def create_ws_body(self, klass, method, data) -> str:
        request_id = self.__get_and_increment_request_id()
        raw_body = OrderedDict([
            ('__class__', "ServerRequest"),
            ('requestData', data),
            ('requestClass', klass),
            ('requestMethod', method),
            ('requestId', request_id)
        ])
        return json.dumps(raw_body, separators=(',', ':'))

    def login(self):
        self.__session, self.initial_response = Login(self.__lang, self.__world).login(ARGS.username, ARGS.password)

    def __get_and_increment_request_id(self):
        request_id = self.__session.cookies['request_id'] + 1
        self.__session.cookies.set('request_id', request_id, path='/', domain='local')
        return request_id

    @staticmethod
    def __sign(body, client_id, signature_key):
        id_ = client_id + signature_key + body
        return hashlib.md5(id_.encode()).hexdigest()[1:11]

    @property
    def cookies(self):
        return self.__session.cookies

    @property
    def headers(self):
        return self.__session.headers
