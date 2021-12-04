import hashlib
import json

import brotli
import yaml
from sqlalchemy import select

from foe_bot.login import Login
from persistent.account import Account
from persistent.db import Session


class Request(object):
    __shared_state = {}

    def __init__(self):
        if not Request.__shared_state:
            self.__dict__ = self.__shared_state
            cfg = self.__load_config()
            self._session, contents = Login(cfg[0]['lang'], cfg[0]['world']).login(cfg[0]['username'],
                                                                                   cfg[0]['password'])

            with Session() as session:
                stmt = select(Account).where(Account.user_name == cfg[0]['username'])
                result = session.execute(stmt).fetchone()
                acc = Account(cfg[0]['username']) if result is None else result[0]
                acc.update_from_response(*contents)
                session.add(acc)
                session.commit()

    def send(self, body):
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

    @staticmethod
    def __load_config():
        with open("../config.yml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.CLoader)
            return cfg

    @staticmethod
    def __sign(body, client_id, signature_key):
        id_ = client_id + signature_key + body
        return hashlib.md5(id_.encode()).hexdigest()[1:11]
