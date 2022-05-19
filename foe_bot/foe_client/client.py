import logging
import os
import pickle
import time

from foe_bot import get_args
from foe_bot.domain.account import Account
from foe_bot.foe_client.log_service import LogService
from foe_bot.foe_client.request import Request
from foe_bot.foe_client.response_mapper import map_to_account
from foe_bot.foe_client.ws_client import WsClient
from foe_bot.service.account_service import AccountService


#  TODO count if send was not success and relog with > 2/10s to reapply city data
class Client:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__shared_state:
            self.__session_file = f"{os.path.dirname(os.path.realpath(__file__))}/../../data/{get_args().username}_session"
            self.__logger: logging.Logger = logging.getLogger(self.__class__.__name__)
            self.__setup()

        self.__relog_in = 0
        self.__is_reload_needed = False

    def send_and_map(self, klass: str, method: str, data) -> (bool, dict):
        body = self.__session.create_rest_body(klass, method, data)
        response, success = self.__session.send(body)  # TODO extract success validation to here
        self.__is_reload_needed = self.__get_reload_need(response)
        map_to_account(self.__acc, *response)
        return success, response

    def save_session(self) -> None:
        os.makedirs(os.path.dirname(self.__session_file), exist_ok=True)
        with open(self.__session_file, 'wb') as req_file:
            pickle.dump(self.__session, req_file)

    def tear_down(self) -> None:
        self.__log_service.stop()
        self.__ws_client.stop()
        self.__log_service.join()
        self.__ws_client.join()

    def relog_in(self):
        if not self.is_connected:
            if os.path.isfile(self.__session_file):
                os.remove(self.__session_file)
            now = int(time.time())
            self.tear_down()
            if self.__relog_in < 0:
                leeway = get_args().relog_waiting_time
                self.__relog_in = now + leeway
                self.__logger.info(f"session expired, relog in {leeway}s")
            elif self.__relog_in < now:
                self.__setup()

    @property
    def is_connected(self) -> bool:
        return self.__ws_client.is_connected and not self.__is_reload_needed

    def __setup(self):
        self.__acc: Account = AccountService().account
        self.__session: Request = self.__load_client()
        map_to_account(self.__acc, *self.__session.initial_response)
        self.__session.initial_response = {}
        self.__ws_client = WsClient(self.__session)
        self.__ws_client.start()
        time.sleep(1)
        self.__log_service = LogService(self.__ws_client, self.__session)
        self.__log_service.start()
        self.__is_reload_needed = False
        if self.is_connected:
            self.__relog_in = -1
        else:
            self.__relog_in = 0

    def __load_client(self) -> Request:
        if os.path.isfile(self.__session_file):
            with open(self.__session_file, 'rb') as req_file:
                session: Request = pickle.load(req_file)
                return session
        else:
            return Request()

    def __get_reload_need(self, response) -> bool:
        for data in response:
            klass = data.get('requestClass', '')
            method = data.get('requestMethod', '')
            if data and klass == 'SessionService' and method == 'getSessionStatus':
                reload_needed = data.get('responseData', dict()).get('isReloadNeeded', False)
                if reload_needed:
                    self.__logger.info("reload session needed")
                return reload_needed

        return False
