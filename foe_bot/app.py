import logging

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map as map_
from foe_bot.ws_client import WsClient

logger = logging.getLogger("as")


def main():
    req = Request()
    acc = map_(Account(), *req.initial_response)
    logger.info("foo")
    token = req._session.cookies['socket_token']
    url = req._session.cookies['socketGatewayUrl']

    ws_client = WsClient(acc, url, token)
    print('ok')
