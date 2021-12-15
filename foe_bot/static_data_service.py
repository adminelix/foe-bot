import json
import logging

import requests

from domain.account import Account


class StaticDataService:
    __shared_state = {}

    def __init__(self, acc: Account):
        self.__dict__ = self.__shared_state
        if not StaticDataService.__shared_state:
            self.__logger = logging.getLogger(self.__class__.__name__)
            self.__acc = acc
            self.__data = {}

    def __get_data(self, identifier: str):
        if identifier not in self.__data.keys():
            url_ = self.__acc.static_data[identifier].url
            response = requests.get(url_)
            json_ = response.json()
            self.__data[identifier] = json_

            self.__logger.info(f"cached {identifier}")
        return self.__data[identifier]

    def find_unit_in_city_entities(self, asset_id: str):
        data = self.__get_data('city_entities')
        for entity in data:
            if asset_id in entity['asset_id']:
                return entity['available_products'][0]
