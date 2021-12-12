import json

from domain.account import Account
from foe_bot.response_mapper import map_to_account as map_


def test_map():
    f = open('content.json')
    data = json.load(f)

    acc = map_(Account(), *data)

    assert len(acc.city_map.entities) == 41
