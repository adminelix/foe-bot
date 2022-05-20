import logging
import math
from concurrent.futures import ThreadPoolExecutor, wait

from foe_bot import get_args
from foe_bot.service.abstract_service import AbstractService
from foe_bot.service.inventory_service import InventoryService
from foe_bot.service.time_service import TimeService


class SnipingService(AbstractService):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__inventory_service = InventoryService()
        self.__auto_snipe_neighbours = get_args().auto_snipe_neighbours
        self.__interval_seconds = 60
        self.__last_scan = 0
        self.__ark_factor: float = 0

    def do(self):
        if self.__ark_factor == 0:
            self.__ark_factor: float = 1 + self.__get_ark_bonus() / 100
        if self.__auto_snipe_neighbours:
            self._snipe_neighbours()

    def _snipe_neighbours(self):
        now = TimeService().time()

        if now > self.__last_scan + self.__interval_seconds:
            self.__last_scan = now
            neighbors = [player for player in self._acc.players.values() if (player.is_neighbor and
                                                                             player.is_active and not
                                                                             player.is_friend and not
                                                                             player.isInvitedFriend and not
                                                                             player.is_guild_member and not
                                                                             player.isInvitedToClan)]

            self.__logger.info('start scanning to snipe')
            with ThreadPoolExecutor(10) as executor:
                futures = [executor.submit(self._scan, neighbour.player_id) for neighbour in neighbors]
                wait(futures)
            self.__logger.info('end scanning to snipe')

    def _scan(self, player_id):
        min_level = 30
        _, res_overview = self._client.send_and_map('GreatBuildingsService', 'getOtherPlayerOverview', [player_id])

        overview = self.extract_overview(res_overview)['responseData']  # great buildings list
        for great_building in overview:
            if great_building['level'] >= min_level:
                _, res_construction = self._client.send_and_map('GreatBuildingsService', 'getConstruction',
                                                                [great_building['entity_id'],
                                                                 great_building['player']['player_id']])
                construction = self.extract_construction(res_construction)['responseData']
                if great_building.get('current_progress', None):  # unlocked
                    profitable = self.calculate(self.__ark_factor, great_building['max_progress'],
                                                great_building['current_progress'], construction)
                    if profitable and profitable['invest'] < self.__inventory_service.sum_of_forge_points() * 0.1:
                        _, success = self._client.send_and_map('GreatBuildingsService', 'contributeForgePoints',
                                                               [great_building['entity_id'],
                                                                great_building['player']['player_id'],
                                                                great_building['level'], profitable['invest'],
                                                                False])
                        if success:
                            self.__logger.info(f"sniped {great_building['player']['name']}'s lvl "
                                               f"{great_building['level']} {great_building['name']} with "
                                               f"{profitable['invest']}fp invest and {profitable['profit']}fp profit "
                                               f"for rank {profitable['rank']}")

    def __get_ark_bonus(self) -> float:
        own_player_id = self._acc.city_user_data.player_id
        _, res_overview = self._client.send_and_map('GreatBuildingsService', 'getOtherPlayerOverview', [own_player_id])
        overview = self.extract_overview(res_overview)['responseData']
        filtered = [entity for entity in overview if 'X_FutureEra_Landmark1' in entity['city_entity_id']]

        if filtered:
            ark = filtered[0]
            _, res_construction = self._client.send_and_map(
                'GreatBuildingsService', 'getConstruction', [ark['entity_id'], own_player_id])
            construction = self.extract_construction(res_construction)['responseData']
            return construction['next_passive_bonus']['value']
        else:
            return 0

    @staticmethod
    def extract_overview(response):
        #  TODO handle if not exact one match
        return [data for data in response if data['requestMethod'] in ['getOtherPlayerOverview']][0]

    @staticmethod
    def extract_construction(response):
        #  TODO handle if not exact one match
        return [data for data in response if data['requestMethod'] in ['getConstruction']][0]

    @staticmethod
    def calculate(ark_factor, max_progress, current_progress, construction):
        for rank in construction['rankings']:
            if not rank.get('reward', None):
                continue
            reward = int(rank['reward']['strategy_point_amount'] * ark_factor)
            invest_to_get = int(math.ceil((max_progress - current_progress) / 2)) + rank.get('forge_points', 0)
            profitable = reward > invest_to_get and invest_to_get + current_progress < max_progress
            if profitable:
                profit = reward - invest_to_get
                return {'rank': rank['rank'], 'profit': profit, 'invest': invest_to_get}
            return None
