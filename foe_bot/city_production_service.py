import logging
import time

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class CityProductionService:

    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger("CityProductionService")

    def pickup(self):
        entities = self.__acc.city_map.entities

        now = int(time.time())

        filtered_keys = [key for (key, value) in entities.items()
                         if 'current_product' in value.state.keys()
                         and ('ProductionFinishedState' == value.state['__class__']
                              or value.state['next_state_transition_at'] <= now)]

        if len(filtered_keys) > 0:
            request_body = self.__request_session.create_rest_body('CityProductionService', 'pickupProduction',
                                                                   [filtered_keys])
            response = self.__request_session.send(request_body)
            self.__logger.info(f"picked up {len(filtered_keys)} building(s)")
            map_to_account(self.__acc, *response)

    # TODO parameterize production time
    # TODO produce if enough resources
    def produce(self):
        types = ['production']  # anything else needs resources check - 'military' for instance
        entities = self.__acc.city_map.entities

        filtered_entities = {key: value for (key, value) in entities.items()
                             if value.type in types
                             and 'IdleState' == value.state['__class__']}

        for value in filtered_entities.values():
            request_body = self.__request_session.create_rest_body('CityProductionService', 'startProduction',
                                                                   [value.id, 1])
            response = self.__request_session.send(request_body)
            map_to_account(self.__acc, *response)

        if len(filtered_entities) > 0:
            self.__logger.info(f"started production for {len(filtered_entities)} building(s)")

    def unlock_unit_slots(self):
        # TODO implement; do only if enough resources
        pass
