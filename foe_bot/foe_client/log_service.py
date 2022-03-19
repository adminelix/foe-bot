import json
import logging
import math
import threading
import time

from foe_bot.foe_client.request import Request
from foe_bot.foe_client.response_mapper import map_to_account
from foe_bot.foe_client.ws_client import WsClient
from foe_bot.service.account_service import AccountService


class LogService(threading.Thread):

    def __init__(self, ws_client: WsClient, request: Request):
        super().__init__()
        self.__shutdown_flag = threading.Event()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__acc = AccountService().account
        self.__ws_client = ws_client
        self.__log_state_interval: int = 300
        self.__last_log_state: int = 0
        self.__log_performance_metrics_interval: int = 3600
        self.__last_log_performance_metrics: int = int(time.time()) + self.__log_performance_metrics_interval
        self.__request_session = request

    def run(self):
        while not self.__shutdown_flag.is_set():
            self.do()
            time.sleep(0.5)

    def do(self):
        self._log_state()
        self._log_performance_metrics()

    def stop(self):
        self.__shutdown_flag.set()

    def _log_state(self):
        reconnects = self.__ws_client.reconnects
        connection_time = self.__ws_client.connection_time
        interval_pools = self.__acc.connection_state_logging.intervalPools  # FIXME set default
        interval = list(interval_pools.values())[0]
        for key in interval_pools.keys():
            interval = interval_pools[key] if self.__round_down(connection_time) > int(key) else interval

        if reconnects >= 0 and connection_time > self.__last_log_state + interval:
            raw_body = self.__get_logstate_body()
            raw_body['connectedTime'] = connection_time
            raw_body['reconnects'] = reconnects

            body = self.__request_session.create_rest_body('LogService', 'logState', [raw_body])
            response, _ = self.__request_session.send(body)
            map_to_account(self.__acc, *response)

            self.__last_log_state = self.__round_down(connection_time)
            self.__logger.info(f'sent socketServer logState with connectedTime: {connection_time} '
                               f'and reconnects: {reconnects}')

    def _log_performance_metrics(self):
        now = int(time.time())
        if now > self.__last_log_performance_metrics + self.__log_performance_metrics_interval:
            raw_body = self.__get_logPerformanceMetrics_body()

            body = self.__request_session.create_rest_body('LogService', 'logPerformanceMetrics', [raw_body])
            response, _ = self.__request_session.send(body)
            map_to_account(self.__acc, *response)

            self.__last_log_performance_metrics = now
            self.__logger.info('sent logPerformanceMetrics')

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

    @staticmethod
    def __round_down(x) -> int:
        return int(math.floor(x / 100.0)) * 100
