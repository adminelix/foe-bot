import json

from sqlalchemy import select

from persistent.account import Account
from persistent.db import Session


def test_process():
    f = open('content.json')
    data = json.load(f)

    acc = Account()
    acc.update_from_response(*data)

    with Session() as session:
        session.add(acc)
        session.commit()

    with Session() as session:
        stmt = select(Account)
        result = session.execute(stmt).fetchone()[0]

        assert result.city_user_data.rank == '63509', 'database access failed'
