import os
import pickle

import pytest

from foe_bot import ARGS
from foe_bot.service.account_service import AccountService

migration_file = f"{os.path.dirname(os.path.realpath(__file__))}/../data_backup/{ARGS.username}_data"


@pytest.mark.skip(reason="just for manually execution to migrate player_logs from one savegame to another")
def test_migrate():
    acc = AccountService().account
    with open(migration_file, 'rb') as acc_file:
        migration_acc = pickle.load(acc_file)

    acc.player_logs = migration_acc.player_logs
    AccountService().save()
