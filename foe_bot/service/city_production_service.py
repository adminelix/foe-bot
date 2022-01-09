import logging
import time

from foe_bot import cfg
from foe_bot.domain.city_map_entity import CityMapEntity
from foe_bot.service.abstract_service import AbstractService
from foe_bot.service.static_data_service import StaticDataService
from foe_bot.util import random_chunk


class CityProductionService(AbstractService):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__static_data_service = StaticDataService()
        self.__config = cfg.get('city_production_service')

    def do(self):
        if self.__config.get('pickup', None):
            self._pickup()
            self._remove_plundered()
        if self.__config.get('unlock_unit_slots', None):
            self._unlock_unit_slots()
        if self.__config.get('produce', None):
            self._produce()

    # TODO take care about if strategy points >= 100 ?
    def _pickup(self):
        types: list[str] = ['production', 'military', 'goods']
        entities = self._acc.city_map.entities
        now = int(time.time())

        filtered_keys = [key for (key, value) in entities.items()
                         if value.type in types and (
                             value.state.next_state_transition_at <= now
                             or value.state.klass == 'ProductionFinishedState')]

        if len(filtered_keys) > 0:
            counter = 0
            chunks = list(random_chunk(filtered_keys, min_chunk=1, max_chunk=10))
            for chunk in chunks:
                success = self._client.send('CityProductionService', 'pickupProduction', [chunk])
                if success:
                    counter += len(chunk)

            if counter > 0:
                self.__logger.info(f"picked up {counter} building(s)")

    def _remove_plundered(self):
        entities = self._acc.city_map.entities

        filtered_keys = [key for (key, value) in entities.items()
                         if value.state.klass in 'PlunderedState']

        if len(filtered_keys) > 0:
            counter = 0
            for key in filtered_keys:
                success = self._client.send('CityProductionService', 'removePlunderedProduction', [key])
                if success:
                    counter += 1
            if counter > 0:
                self.__logger.info(f"removed plundered state from {counter} building(s)")

    # TODO parameterize production time
    def _produce(self):
        now = int(time.time())
        types: list[str] = ['production', 'military', 'goods']
        budget_factor: float = 0.1
        counter: int = 0
        entities: dict[int, CityMapEntity] = self._acc.city_map.entities

        filtered_entities = {key: value for (key, value) in entities.items()
                             if value.type in types
                             and value.connected > 0
                             and (value.state.klass == 'IdleState'
                                  or value.state.next_state_transition_at < now)}

        for value in filtered_entities.values():
            if value.type == 'production':
                success = self._client.send('CityProductionService', 'startProduction', [value.id, 1])
                if success:
                    counter += 1

            elif value.type == 'goods':
                slot = 0
                product = self.__static_data_service.find_available_products_in_city_entities(value.cityentity_id)[slot]
                costs = product['requirements']['cost']['resources']

                if (costs['money'] < self._acc.resources.money * budget_factor
                    and costs['supplies'] < self._acc.resources.supplies * budget_factor):
                    success = self._client.send('CityProductionService', 'startProduction', [value.id, slot + 1])
                    if success:
                        counter += 1

            elif value.type == 'military':  # if military building
                for slot in value.unitSlots:
                    if slot['unit_id'] < 0 and slot['unlocked']:  # has empty slot
                        unit = self.__static_data_service.find_available_products_in_city_entities(value.cityentity_id)[
                            0]
                        costs = unit['requirements']['cost']['resources']

                        #  can you afford
                        if (costs['money'] < self._acc.resources.money * budget_factor
                            and costs['supplies'] < self._acc.resources.supplies * budget_factor
                            and costs['population'] < self._acc.resources.population * budget_factor
                            and costs['premium'] == 0):
                            nr_ = 0 if 'nr' not in slot.keys() else slot['nr']
                            success = self._client.send('CityProductionService', 'startProduction',
                                                        [value.id, nr_])
                            if success:
                                counter += 1
                            break

        if counter > 0:
            self.__logger.info(f"started production for {counter} building(s)")

    def _unlock_unit_slots(self):
        budget_factor = 0.1
        entities = self._acc.city_map.entities

        for value in entities.values():
            if value.type == 'military' and value.connected > 0:
                for slot in value.unitSlots:
                    if (not slot['unlocked']
                        and slot['is_unlockable']
                        and slot['unlockCosts']['resources']['premium'] == 0
                        and slot['unlockCosts']['resources']['money'] <= self._acc.resources.money * budget_factor
                        and slot['unlockCosts']['resources'][
                            'supplies'] <= self._acc.resources.supplies + budget_factor):
                        # TODO what is the meaning of 0 in request body? - it was 0 at everytime
                        success = self._client.send('CityProductionService', 'unlockSlot',
                                                    [slot['entity_id'], slot['nr'], 0])

                        if success:
                            self.__logger.info(f"unlocked slot {slot['nr']} for buidling {value.cityentity_id}")
