from pytest_assert_utils import util

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


def test_sample_request():
    """
    [
      {
        "__class__": "ServerRequest",
        "requestData": [],
        "requestClass": "InventoryService",
        "requestMethod": "getItems",
        "requestId": 7
      }
    ]
    """
    req = Request()

    acc = map_to_account(Account(), *req.initial_response)

    body = req.create_body('InventoryService', 'getItems', [])
    resp = req.send(body)
    flat = [value for elem in resp
            for value in elem.values()]

    assert util.List.containing('InventoryService') == flat, "login failed: %s" % resp
