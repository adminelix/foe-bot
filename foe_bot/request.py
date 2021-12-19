import hashlib
import json
import logging
import os
import pickle
import time

from requests import Session

from domain.account import Account
from foe_bot import cfg
from foe_bot.exceptions import RequestException
from foe_bot.login import Login
from foe_bot.response_mapper import map_to_account
from foe_bot.util import foe_json_loads
from foe_bot.ws_client import WsClient

session_file = f"../data/{cfg['username']}_session"


def load_session() -> Session:
    if os.path.isfile(session_file):
        with open(session_file, 'rb') as req_file:
            return pickle.load(req_file)
    else:
        return Request()


def save_session(req: Session) -> None:
    os.makedirs(os.path.dirname(session_file), exist_ok=True)
    with open(session_file, 'wb') as req_file:
        pickle.dump(req, req_file)


class Request(object):
    __shared_state = {}

    def __init__(self, acc: Account):
        self.__dict__ = self.__shared_state
        if not Request.__shared_state:
            self.__logger: logging.Logger = logging.getLogger("Request")
            self.__wait_between_req: float = 0.5
            self.__acc: Account = acc
            self.__session: Session
            self.ws_client: WsClient
            self.__login(acc)

    def __login(self, acc: Account):
        self.__session, initial_response = Login(cfg['lang'], cfg['world']).login(cfg['username'], cfg['password'])
        map_to_account(acc, *initial_response)

        token = self.__session.cookies['socket_token']
        url = self.__session.cookies['socketGatewayUrl']
        self.ws_client = WsClient(self.__acc, url, token, self.__session.cookies, self.__session.headers)
        self.ws_client.start()

    def send(self, body: str):
        successful: bool = True
        signature = self.__sign(body, self.__session.cookies.get('clientId'), self.__session.cookies.get('signature_key'))
        query = {'h': self.__session.cookies.get('clientId')}
        header = {'Signature': signature}

        response = self.__session.post('https://de14.forgeofempires.com/game/json', data=body, params=query,
                                       headers=header)
        if not (response.status_code == 200):
            raise RequestException("Did not get a 200 response code: %s" % response.content)

        content = response.content.decode()

        lower = content.lower()
        if 'error' in lower or 'exception' in lower:
            successful = False
            self.__logger.error(f"request failed > request:'{body}', response:'{content}'")

        time.sleep(self.__wait_between_req)
        return foe_json_loads(content), successful

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
        request_id = self.__session.cookies['request_id'] + 1
        self.__session.cookies.set('request_id', request_id, path='/', domain='local')
        return request_id

    @staticmethod
    def __sign(body, client_id, signature_key):
        id_ = client_id + signature_key + body
        return hashlib.md5(id_.encode()).hexdigest()[1:11]
