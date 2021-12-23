import json

from pytest_assert_utils import util

from foe_bot.domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


def test_sample_request():
    req = Request()
    acc = map_to_account(Account(), *req.initial_response)

    json.dumps(req.initial_response)
    with open('test_startup.json', 'w') as file:
        file.write(json.dumps(req.initial_response))

    body = req.create_rest_body('InventoryService', 'getItems', [])
    resp = req.send(body)
    flat = [value for elem in resp
            for value in elem.values()]

    assert util.List.containing('InventoryService') == flat, "login failed: %s" % resp
