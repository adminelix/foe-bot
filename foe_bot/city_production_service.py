import logging
import time

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account
from foe_bot.util import random_chunk


class CityProductionService:

    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger("CityProductionService")

    # TODO take care about if strategy points >= 100 ?
    def pickup(self):
        entities = self.__acc.city_map.entities

        now = int(time.time())

        filtered_keys = [key for (key, value) in entities.items()
                         if 'current_product' in value.state.keys()
                         and ('ProductionFinishedState' == value.state['__class__']
                              or value.state['next_state_transition_at'] <= now)]

        if len(filtered_keys) > 0:
            chunks = list(random_chunk(filtered_keys, min_chunk=1, max_chunk=10))
            for chunk in chunks:
                request_body = self.__request_session.create_rest_body('CityProductionService', 'pickupProduction',
                                                                       [chunk])
                response = self.__request_session.send(request_body)
                map_to_account(self.__acc, *response)
            self.__logger.info(f"picked up {len(filtered_keys)} building(s)")

    # TODO parameterize production time
    # TODO produce if enough resources
    def produce(self):
        # [
        #     {
        #         "__class__": "ServerRequest",
        #         "requestData": [
        #             36,
        #             1
        #         ],
        #         "requestClass": "CityProductionService",
        #         "requestMethod": "startProduction",
        #         "requestId": 29
        #     }
        # ]
        types = ['production']  # anything else needs resources check - 'military' for instance
        entities = self.__acc.city_map.entities

        filtered_entities = {key: value for (key, value) in entities.items()
                             if value.type in types
                             and value.connected > 0
                             and 'IdleState' == value.state['__class__']}

        for value in filtered_entities.values():
            request_body = self.__request_session.create_rest_body('CityProductionService', 'startProduction',
                                                                   [value.id, 1])
            response = self.__request_session.send(request_body)
            map_to_account(self.__acc, *response)

        if len(filtered_entities) > 0:
            self.__logger.info(f"started production for {len(filtered_entities)} building(s)")

    def unlock_unit_slots(self):
        budget_factor = 0.1
        entities = self.__acc.city_map.entities

        for value in entities.values():
            if value.type == 'military' and value.connected > 0:
                for slot in value.unitSlots:
                    if (not slot['unlocked']
                        and slot['is_unlockable']
                        and slot['unlockCosts']['resources']['premium'] == 0
                        and slot['unlockCosts']['resources']['money'] <= self.__acc.resources.money * budget_factor
                        and slot['unlockCosts']['resources'][
                            'supplies'] <= self.__acc.resources.supplies + budget_factor):
                        # TODO what is the meaning of 0 in request body?
                        request_body = self.__request_session.create_rest_body('CityProductionService', 'unlockSlot',
                                                                               [slot['entity_id'], slot['nr'], 0])
                        response = self.__request_session.send(request_body)
                        slot['unlocked'] = response['responseData']
