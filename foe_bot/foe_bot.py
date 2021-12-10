from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map as map_


def main():
    req = Request()
    acc = map_(Account(), *req.initial_response)

    print('ok')
