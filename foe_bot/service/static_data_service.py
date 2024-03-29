import logging

import requests

from foe_bot.service.account_service import AccountService


class StaticDataService:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not StaticDataService.__shared_state:
            self.__logger = logging.getLogger(self.__class__.__name__)
            self.__acc = AccountService().account
            self.__data = {}

    def get_data(self, identifier: str):
        if identifier not in self.__data.keys():
            url_ = self.__acc.static_data[identifier].url
            response = requests.get(url_)
            json_ = response.json()
            self.__data[identifier] = json_

            self.__logger.info(f"cached {identifier}")
        return self.__data[identifier]

    def find_available_products_in_city_entities(self, asset_id: str):
        data = self.get_data('city_entities')
        for entity in data:
            if asset_id in entity['asset_id']:
                return entity['available_products']
