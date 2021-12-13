import json

from pytest_assert_utils import util

from foe_bot.request import Request


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

    json.dumps(req.initial_response)
    with open('test_startup.json', 'w') as file:
        file.write(json.dumps(req.initial_response))

    body = req.create_rest_body('InventoryService', 'getItems', [])
    resp = req.send(body)
    flat = [value for elem in resp
            for value in elem.values()]

    assert util.List.containing('InventoryService') == flat, "login failed: %s" % resp
