import os
import pickle

from foe_bot import get_args
from foe_bot.domain.account import Account
from foe_bot.domain.hidden_reward import HiddenReward


class AccountService:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__shared_state:
            self.__data_file = f"{os.path.dirname(os.path.realpath(__file__))}/../../data/{get_args().username}_data"
            self.__account = self.__load_account()
            self.__account.hidden_rewards = dict[int, HiddenReward]()

    def __load_account(self) -> Account:
        if os.path.isfile(self.__data_file):
            with open(self.__data_file, 'rb') as acc_file:
                return pickle.load(acc_file)
        else:
            return Account()

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.__data_file), exist_ok=True)
        with open(self.__data_file, 'wb') as acc_file:
            pickle.dump(self.__account, acc_file)

    @property
    def account(self) -> Account:
        return self.__account
