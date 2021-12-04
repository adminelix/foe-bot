from pytest_assert_utils import util
from sqlalchemy import select

from foe_bot.request import Request
from persistent.account import Account
from persistent.db import Session


def test_sample_request():
    body = '[{"__class__":"ServerRequest","requestData":[],"requestClass":"InventoryService","requestMethod":"getItems","requestId":7}]'
    req = Request()

    resp = req.send(body)
    flat = [value for elem in resp
            for value in elem.values()]

    assert util.List.containing('InventoryService') == flat, "login failed: %s" % resp

    with Session() as session:
        stmt = select(Account).where(Account.user_name == "testibo2")
        result = session.execute(stmt).fetchone()[0]
        assert result.city_user_data.user_name == 'testibo2', 'storing initial data to db failed'
