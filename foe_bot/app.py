import logging
import time

from domain.account import Account
from foe_bot.LogService import LogService
from foe_bot.city_production_service import CityProductionService
from foe_bot.hidden_reward_service import HiddenRewardService
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account as map_
from foe_bot.static_data_service import StaticDataService
from foe_bot.ws_client import WsClient

logger = logging.getLogger("as")


# TODO simulate human play times
# TODO react on SIGINT and shutdown ws_client
def main():
    req = Request()
    acc = map_(Account(), *req.initial_response)

    token = req._session.cookies['socket_token']
    url = req._session.cookies['socketGatewayUrl']
    ws_client = WsClient(acc, url, token)
    ws_client.run()

    cps = CityProductionService(acc)
    hrs = HiddenRewardService(acc)
    ls = LogService(acc, ws_client)
    StaticDataService(acc)

    while True:
        ls.log_state()
        ls.log_performance_metrics()
        cps.pickup()
        cps.produce()
        hrs.collect()

        time.sleep(10)

    ws_client.stop()
