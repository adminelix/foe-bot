import logging
import math

from foe_bot import get_args
from foe_bot.service.abstract_service import AbstractService


class SnipingService(AbstractService):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__auto_snipe_neighbours = get_args().auto_snipe_neighbours
        # self.__interval_seconds = 60

    def do(self):
        if self.__auto_snipe_neighbours:
            self._search()

    def _search(self):
        resp = self._client.send('RankingService', 'searchRanking',
                                 ["players", None, self._acc.city_user_data.user_name, True, ''])
        ranking = self.extract_ranking(resp)
        length = ranking['responseData']['length']
        page_size = len(ranking['responseData']['rankings'])
        pages = int(length / page_size)
        result = list()

        # executor = concurrent.futures.ProcessPoolExecutor(10)
        # futures = [executor.submit(try_my_operation, item) for item in items]
        # concurrent.futures.wait(futures)

        for i in range(pages):
            self.__logger.info(f"page {i}")
            resp = self._client.send('RankingService', 'getRanking', ["players", 'null', i])
            ranking = self.extract_ranking(resp)
            for rank in ranking['responseData']['rankings']:
                resp = self._client.send('GreatBuildingsService', 'getOtherPlayerOverview',
                                         [rank['player']['player_id']])

                overview = self.extract_overview(resp)['responseData']  # great buildings list
                for great_building in overview:
                    if great_building['level'] >= 30:
                        resp = self._client.send('GreatBuildingsService', 'getConstruction',
                                                 [great_building['entity_id'], great_building['player']['player_id']])
                        construction = self.extract_construction(resp)['responseData']
                        if great_building.get('current_progress', None):  # unlocked
                            res = self.calculate(great_building['max_progress'], great_building['current_progress'],
                                                 construction)
                            if res:
                                res['great_building'] = great_building
                                result.append(res)
                            pass

    @staticmethod
    def extract_ranking(resp):
        #  TODO handle if not exact one match
        return [data for data in resp if data['requestMethod'] in ['searchRanking', 'getRanking']][0]

    @staticmethod
    def extract_overview(resp):
        #  TODO handle if not exact one match
        return [data for data in resp if data['requestMethod'] in ['getOtherPlayerOverview']][0]

    @staticmethod
    def extract_construction(resp):
        #  TODO handle if not exact one match
        return [data for data in resp if data['requestMethod'] in ['getConstruction']][0]

    @staticmethod
    def calculate(max_progress, current_progress, construction):
        ark_factor = 1.9

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
