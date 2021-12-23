import json
import logging
import time

from foe_bot.domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account
from foe_bot.ws_client import WsClient


class LogService:

    def __init__(self, acc: Account, ws_client: WsClient):
        self.__acc = acc
        self.__ws_client = ws_client
        self.__log_state_interval: int = 300
        self.__last_log_state: int = 0
        self.__log_performance_metrics_interval: int = 3600
        self.__last_log_performance_metrics: int = int(time.time()) + self.__log_performance_metrics_interval
        self.__request_session = Request()
        self.__logger = logging.getLogger(self.__class__.__name__)

    def log_state(self):
        reconnects = self.__ws_client.reconnects
        connection_time = self.__ws_client.connection_time
        # doubles interval if socket is connected longer than 900s
        interval = self.__log_state_interval if connection_time < 900 else 2 * self.__log_state_interval

        if reconnects >= 0 and connection_time > self.__last_log_state + interval:
            raw_body = self.__get_logstate_body()
            raw_body['connectedTime'] = connection_time
            raw_body['reconnects'] = reconnects

            body = self.__request_session.create_rest_body('LogService', 'logState', [raw_body])
            response, _ = self.__request_session.send(body)
            map_to_account(self.__acc, *response)

            self.__last_log_state = int(time.time())
            self.__logger.info(f'sent socketServer logState with connectedTime: {connection_time} '
                               f'and reconnects: {reconnects}')

    def log_performance_metrics(self):
        now = int(time.time())
        if now > self.__last_log_performance_metrics + self.__log_performance_metrics_interval:
            raw_body = self.__get_logPerformanceMetrics_body()

            body = self.__request_session.create_rest_body('LogService', 'logPerformanceMetrics', [raw_body])
            response, _ = self.__request_session.send(body)
            map_to_account(self.__acc, *response)

            self.__last_log_performance_metrics = now
            self.__logger.info(f'sent logPerformanceMetrics')

    @staticmethod
    def __get_logstate_body():
        string = """
         {
            "__class__": "ConnectionState",
            "state": 2,
            "componentId": "socketServer",
            "connectedTime": 906,
            "reconnects": 0
        }"""
        return json.loads(string)

    @staticmethod
    def __get_logPerformanceMetrics_body():
        string = """
       {
            "__class__": "FPSPerformance",
            "module": "City",
            "fps": 25,
            "vram": 0
        }"""
        return json.loads(string)
