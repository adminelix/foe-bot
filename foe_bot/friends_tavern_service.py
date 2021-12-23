import json
import logging

from foe_bot.domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class FriendsTavernService:
    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger("FriendsTavernService")
        if not self.__acc.own_tavern:
            self.refresh_own_tavern()

    def refresh_own_tavern(self):
        request_body = self.__request_session.create_rest_body('FriendsTavernService', 'getOwnTavern', [])
        response, _ = self.__request_session.send(request_body)
        map_to_account(self.__acc, *response)

    def collect(self):
        own_tavern_state = self.__acc.other_tavern_states.get(self.__acc.city_user_data.player_id, None)
        if own_tavern_state and own_tavern_state.unlockedChairCount == own_tavern_state.sittingPlayerCount:
            request_body = self.__request_session.create_rest_body('FriendsTavernService', 'collectReward', [])
            response, success = self.__request_session.send(request_body)
            if success:
                map_to_account(self.__acc, *response)
                self.__logger.info("collected tavern rewards")
                self.refresh_own_tavern()

    def visit(self):
        states = self.__acc.other_tavern_states
        player_ids_to_visit = [state.ownerId for state in states.values() if
                               not state.state and state.sittingPlayerCount < state.unlockedChairCount]
        visited = 0
        for id in player_ids_to_visit:
            request_body = self.__request_session.create_rest_body('FriendsTavernService', 'getOtherTavern', [id])
            response, success = self.__request_session.send(request_body)
            map_to_account(self.__acc, *response)
            sat_down = 'satdown' in json.dumps(response).lower()
            if success and sat_down:
                visited += 1

        if visited > 0:
            self.__logger.info(f"visited {visited} friend taverns")

    def extend_tavern(self):
        # TODO implement
        pass
