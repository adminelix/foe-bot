import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor, wait
from textwrap import dedent

from foe_bot import get_args
from foe_bot.service import telegram_send
from foe_bot.service.abstract_service import AbstractService
from foe_bot.service.inventory_service import InventoryService


class SnipingService(AbstractService):

    def __init__(self):
        super().__init__()
        self.__logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.__inventory_service: InventoryService = InventoryService()
        self.__auto_snipe_neighbours: bool = get_args().auto_snipe_neighbours
        self.__player_ids_to_snipe: list[int] = self.resolve_player_ids()
        self.__calculated_great_buildings: dict[str, dict] = dict[str, dict]()
        self.__neighbor_interval_seconds: int = 60
        self.__neighbor_last_scan: int = 0
        self.__player_interval_seconds: int = 10
        self.__player_last_scan: int = 0
        self.__ark_factor: float = 0

    def do(self):
        if self.__ark_factor == 0:
            self.__ark_factor: float = 1 + self.__get_ark_bonus() / 100
        if self.__auto_snipe_neighbours:
            self._snipe_neighbours()
        if self.__player_ids_to_snipe:
            self._scan_players_to_snipe()

    def _snipe_neighbours(self):
        now = int(time.time())

        if now > self.__neighbor_last_scan + self.__neighbor_interval_seconds:
            self.__neighbor_last_scan = now - 1
            neighbors = [player for player in self._acc.players.values() if (player.is_neighbor and
                                                                             player.is_active and not
                                                                             player.is_friend and not
                                                                             player.isInvitedFriend and not
                                                                             player.is_guild_member and not
                                                                             player.isInvitedToClan)]

            with ThreadPoolExecutor(10) as executor:
                futures = [executor.submit(self._scan, neighbour.player_id) for neighbour in neighbors]
                wait(futures)
            great_buildings = [future.result() for future in futures if future.result()]
            great_buildings.sort(reverse=True, key=lambda x: x['calculation']['profit'])

            for great_building in great_buildings:
                calculation = great_building['calculation']
                if great_building and calculation['invest'] < self.__inventory_service.sum_of_forge_points() * 0.1:
                    _, success = self._client.send_and_map('GreatBuildingsService', 'contributeForgePoints',
                                                           [great_building['entity_id'],
                                                            great_building['player']['player_id'],
                                                            great_building['level'], calculation['invest'],
                                                            False])
                    if success:
                        self.__logger.info(f"sniped {great_building['player']['name']}'s lvl "
                                           f"{great_building['level']} {great_building['name']} with "
                                           f"{calculation['invest']}fp invest and {calculation['profit']}fp profit "
                                           f"for rank {calculation['rank']}")

    def _scan_players_to_snipe(self):
        now = int(time.time())
        if now > self.__player_last_scan + self.__player_interval_seconds:
            self.__player_last_scan = now - 1

            with ThreadPoolExecutor(10) as executor:
                futures = [executor.submit(self._scan, player_id) for player_id in self.__player_ids_to_snipe]
                wait(futures)
            great_buildings = [future.result() for future in futures if future.result()]

            for great_building in great_buildings:
                calculation = great_building['calculation']
                great_building['hash'] = hash(frozenset(calculation))
                stored_gb_id = f"{great_building['player']['player_id']}.{great_building['entity_id']}"
                stored_gb = self.__calculated_great_buildings.get(stored_gb_id, None)

                if not stored_gb or stored_gb['hash'] != great_building['hash']:
                    text = dedent(f"""\
                    could snipe '{great_building['player']['name']}'s level {great_building['level']}
                    '{great_building['name']}' with {calculation['invest']}fp invest and {calculation['profit']}fp
                    profit for rank {calculation['rank']}""").replace('\n', ' ')

                    self.__logger.info(text)
                    telegram_send(f"{text} on world {get_args().world}")
                    self.__calculated_great_buildings[stored_gb_id] = great_building

    def resolve_player_ids(self):
        player_ids = [self._get_player_id(player_name.strip(' '))
                      for player_name in get_args().players_to_snipe.split(',')]
        player_ids = [player_id for player_id in player_ids if player_id]
        return player_ids

    def _get_player_id(self, player_name):
        try:
            success, res_search = self._client.send_and_map('RankingService', 'searchRanking',
                                                            ["players", "null", player_name, False, ""])
            search = self.extract_response(res_search, 'searchRanking')['responseData']
            player = [player['player'] for player in search['rankings'] if player['player']['name'] == player_name][0]
            return player['player_id']
        except Exception:
            self.__logger.warning(f"no player with name '{player_name}' identified")

    def _scan(self, player_id):
        min_level = 30
        _, res_overview = self._client.send_and_map('GreatBuildingsService', 'getOtherPlayerOverview', [player_id])

        overview = self.extract_response(res_overview, 'getOtherPlayerOverview')['responseData']  # great buildings list
        for great_building in overview:
            if great_building.get('level', 1) >= min_level:
                _, res_construction = self._client.send_and_map('GreatBuildingsService', 'getConstruction',
                                                                [great_building['entity_id'],
                                                                 great_building['player']['player_id']])
                construction = self.extract_response(res_construction, 'getConstruction')['responseData']
                if great_building.get('current_progress', None):  # unlocked
                    calculation = self.calculate(self.__ark_factor, great_building['max_progress'],
                                                 great_building['current_progress'], construction)
                    if calculation:
                        great_building['calculation'] = calculation
                        return great_building

    def __get_ark_bonus(self) -> float:
        own_player_id = self._acc.city_user_data.player_id
        _, res_overview = self._client.send_and_map('GreatBuildingsService', 'getOtherPlayerOverview', [own_player_id])
        overview = self.extract_response(res_overview, 'getOtherPlayerOverview')['responseData']
        filtered = [entity for entity in overview if 'X_FutureEra_Landmark1' in entity['city_entity_id']]

        if filtered:
            ark = filtered[0]
            _, res_construction = self._client.send_and_map(
                'GreatBuildingsService', 'getConstruction', [ark['entity_id'], own_player_id])
            construction = self.extract_response(res_construction, 'getConstruction')['responseData']
            return construction['next_passive_bonus']['value']
        else:
            return 0

    @staticmethod
    def extract_response(response, request_method):
        #  TODO handle if not exact one match
        return [data for data in response if data['requestMethod'] == request_method][0]

    @staticmethod
    def calculate(ark_factor, max_progress, current_progress, construction):
        for rank in construction['rankings']:
            if not rank.get('reward', None):
                continue
            reward = int(rank['reward']['strategy_point_amount'] * ark_factor)
            invest_to_get = int(math.ceil((max_progress - current_progress + rank.get('forge_points', 0)) / 2))
            profitable = reward > invest_to_get and invest_to_get + current_progress < max_progress
            if profitable:
                profit = reward - invest_to_get
                return {'rank': rank['rank'], 'profit': profit, 'invest': invest_to_get}
            return None
