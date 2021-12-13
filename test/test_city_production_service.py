import json

from domain.account import Account
from foe_bot.city_production_service import CityProductionService
from foe_bot.response_mapper import map_to_account


def test_gather():
    f = open('foobar3.json')
    data = json.load(f)

    acc = map_to_account(Account(), *data)

    cps = CityProductionService(acc)
    cps.produce()
    pass
