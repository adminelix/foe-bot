import time

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account as map_
from foe_bot.ws_client import WsClient


def test_run():
    req = Request()

    acc = map_(Account(), *req.initial_response)
    token = req._session.cookies['socket_token']
    url = req._session.cookies['socketGatewayUrl']

    with WsClient(acc, url, token) as ws_client:
        start = time.time()
        while not ws_client.is_connected and time.time() - start < 10:
            time.sleep(0.1)

        assert ws_client.is_connected
