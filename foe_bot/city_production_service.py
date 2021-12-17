import logging
import time

from domain.account import Account
from domain.city_map_entity import CityMapEntity
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account
from foe_bot.static_data_service import StaticDataService
from foe_bot.util import random_chunk


class CityProductionService:

    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__static_data_service = StaticDataService(acc)
        self.__logger = logging.getLogger("CityProductionService")

    # TODO take care about if strategy points >= 100 ?
    def pickup(self):
        entities = self.__acc.city_map.entities

        now = int(time.time())

        filtered_keys = [key for (key, value) in entities.items()
                         if value.state.current_product
                         and (value.state.klass == 'ProductionFinishedState'
                              or value.state.next_state_transition_at <= now)]

        if len(filtered_keys) > 0:
            chunks = list(random_chunk(filtered_keys, min_chunk=1, max_chunk=10))
            for chunk in chunks:
                request_body = self.__request_session.create_rest_body('CityProductionService', 'pickupProduction',
                                                                       [chunk])
                response = self.__request_session.send(request_body)
                map_to_account(self.__acc, *response)
            self.__logger.info(f"picked up {len(filtered_keys)} building(s)")

    # TODO parameterize production time
    def produce(self):
        types: list[str] = ['production', 'military']  # anything else needs resources check - 'military' for instance
        budget_factor: float = 0.1
        counter: int = 0
        entities: dict[int, CityMapEntity] = self.__acc.city_map.entities

        filtered_entities = {key: value for (key, value) in entities.items()
                             if value.type in types
                             and value.connected > 0
                             and value.state.klass == 'IdleState'}

        for value in filtered_entities.values():
            if value.type == 'production':
                request_body = self.__request_session.create_rest_body('CityProductionService', 'startProduction',
                                                                       [value.id, 1])
                response = self.__request_session.send(request_body)
                map_to_account(self.__acc, *response)
                counter += 1

            elif value.type == 'military':  # if military building
                for slot in value.unitSlots:
                    if slot['unit_id'] < 0 and slot['unlocked']:  # has empty slot
                        unit = self.__static_data_service.find_unit_in_city_entities(value.cityentity_id)
                        costs = unit['requirements']['cost']['resources']

                        #  can you afford
                        if (costs['money'] < self.__acc.resources.money * budget_factor
                            and costs['supplies'] < self.__acc.resources.supplies * budget_factor
                            and costs['population'] < self.__acc.resources.population * budget_factor
                            and costs['premium'] == 0):
                            nr_ = 0 if 'nr' not in slot.keys() else slot['nr']
                            request_body = self.__request_session.create_rest_body('CityProductionService',
                                                                                   'startProduction',
                                                                                   [value.id, nr_])
                            response = self.__request_session.send(request_body)
                            map_to_account(self.__acc, *response)
                            counter += 1
                            break

        if counter > 0:
            self.__logger.info(f"started production for {counter} building(s)")

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
                        # TODO what is the meaning of 0 in request body - it was 0 at everytime?
                        request_body = self.__request_session.create_rest_body('CityProductionService', 'unlockSlot',
                                                                               [slot['entity_id'], slot['nr'], 0])
                        response = self.__request_session.send(request_body)
                        map_to_account(self.__acc, *response)

                        self.__logger.info(f"unlocked slot {slot['nr']} for buidling {value.cityentity_id}")
