from pytest_assert_utils import util

from foe_bot.request import Request


def test_sample_request():
    body = '[{"__class__":"ServerRequest","requestData":[],"requestClass":"InventoryService","requestMethod":"getItems","requestId":7}]'
    req = Request()

    resp = req.send(body)
    flat = [value for elem in resp
            for value in elem.values()]

    assert util.List.containing('InventoryService') == flat, "login failed: %s" % resp
