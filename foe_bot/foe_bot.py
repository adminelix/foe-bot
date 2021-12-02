import json

from sqlalchemy.orm import session

from persistent.account import Account
from persistent.db import Session
import persistent.deploy


def main():

    f = open('content.json')
    data = json.load(f)

    # req = Request()
    # sample_request(req)
    account = Account()
    for item in data:
        account.populate(**item)

    account.id = 1235324
    account.player_id = 23487
    account.user_name = 'foo'

    with Session() as session1:
        session1.add(account)
        session1.commit()

    foo: session = Session()

    print('ok')
