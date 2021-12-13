import logging
import time

from domain.account import Account
from foe_bot.city_production_service import CityProductionService
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account as map_
from foe_bot.ws_client import WsClient

logger = logging.getLogger("as")


def main():
    req = Request()
    acc = map_(Account(), *req.initial_response)

    token = req._session.cookies['socket_token']
    url = req._session.cookies['socketGatewayUrl']
    ws_client = WsClient(acc, url, token)
    ws_client.run()

    while True:
        cps = CityProductionService(acc)
        cps.pickup()
        cps.produce()

        time.sleep(10)

    ws_client.stop()
