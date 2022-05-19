import re
import time as time_

from foe_bot.service.account_service import AccountService


class InventoryService:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__shared_state:
            self.__acc = AccountService().account

    def sum_of_forge_points(self) -> int:
        fp_packages = [item for item in self.__acc.inventory_items.values()
                       if re.match(r".+_forgepoints", item.itemAssetName)]
        fp: int = 0
        for fp_package in fp_packages:
            fp = fp + fp_package.inStock * fp_package.item.resource_package.gain
        return fp + self.__acc.resources.strategy_points
