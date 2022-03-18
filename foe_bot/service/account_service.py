import os
import pickle

from foe_bot import ARGS
from foe_bot.domain.account import Account

data_file = f"{os.path.dirname(os.path.realpath(__file__))}/../../data/{ARGS.username}_data"


class AccountService:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__shared_state:
            self.__account = self.__load_account()

    @classmethod
    def __load_account(cls) -> Account:
        if os.path.isfile(data_file):
            with open(data_file, 'rb') as acc_file:
                return pickle.load(acc_file)
        else:
            return Account()

    def save(self) -> None:
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'wb') as acc_file:
            pickle.dump(self.__account, acc_file)

    @property
    def account(self) -> Account:
        return self.__account
