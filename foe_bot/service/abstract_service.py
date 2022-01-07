import abc
from abc import abstractmethod

from foe_bot.domain.account import Account
from foe_bot.foe_client.client import Client
from foe_bot.service.account_service import AccountService


class AbstractService(abc.ABC):
    __abstract__ = True

    def __init__(self):
        self._acc: Account = AccountService().account
        self._client: Client = Client()

    @abstractmethod
    def do(self) -> None:
        pass
