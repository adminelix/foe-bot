import time as time_

from foe_bot.service.account_service import AccountService


class TimeService:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__shared_state:
            self.__acc = AccountService().account

    def time(self) -> int:
        return int(time_.time()) - self.__acc.time.diff
