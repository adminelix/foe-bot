import json

from sqlalchemy import select

from domain.account import Account
from domain.city_map_entity import CityMapEntity
from domain.city_user_data import custom_decoder
from domain.db import Session


def test_process():
    f = open('content.json')
    data = json.load(f)

    with Session() as session:
        acc = Account('testibo2')
        session.add(acc)
        acc.update_from_response(*data)
        session.commit()

    with Session() as session:
        stmt = select(Account).where(Account.user_name == "testibo2")
        result = session.execute(stmt).fetchone()[0]

        session.add(result)

        result.city_map.entities.append(CityMapEntity())

        ent = session.query(CityMapEntity).all()

        assert result.city_user_data.rank == '63509', 'database access failed'


def test_process2():
    f = open('content.json')
    data = json.load(f)

    data_ = json.dumps(data[32])
    foo = json.loads(data_, object_hook=custom_decoder)
