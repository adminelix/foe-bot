import time

from foe_bot.foe_client.request import Request
from foe_bot.foe_client.response_mapper import map_to_account
from foe_bot.foe_client.ws_client import WsClient
from foe_bot.service.account_service import AccountService
from test import set_args

set_args()


def test_run():
    req = Request()
    map_to_account(AccountService().account, *req.initial_response)

    ws_client = WsClient(req)
    ws_client.start()
    start = time.time()
    while not ws_client.is_connected and time.time() - start < 100000:
        time.sleep(0.1)

    assert ws_client.is_connected
    ws_client.stop()
    ws_client.join()
