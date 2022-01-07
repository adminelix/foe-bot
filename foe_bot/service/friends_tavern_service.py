import logging
import time

from foe_bot.service.abstract_service import AbstractService


class FriendsTavernService(AbstractService):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__last_refresh = 0
        self.__refresh_interval = 15 * 60  # in seconds
        self.__refresh_own_tavern(False)

    def do(self):
        self._collect()
        self._visit()

    def _collect(self):
        own_tavern_state = self._acc.other_tavern_states.get(self._acc.city_user_data.player_id, None)

        if own_tavern_state and own_tavern_state.unlockedChairCount == own_tavern_state.sittingPlayerCount:
            success = self._client.send('FriendsTavernService', 'collectReward', [])

            if success:
                self.__logger.info("collected tavern rewards")

            self.__refresh_own_tavern(True)

    def _visit(self):
        states = self._acc.other_tavern_states
        player_ids_to_visit = [state.ownerId for state in states.values() if
                               not state.state and state.sittingPlayerCount < state.unlockedChairCount]
        counter = 0
        for id_ in player_ids_to_visit:
            success = self._client.send('FriendsTavernService', 'getOtherTavern', [id_])

            if success:
                counter += 1

        if counter > 0:
            self.__logger.info(f"visited {counter} friend taverns")

    def __refresh_own_tavern(self, force: bool):
        now = int(time.time())
        if force or now > self.__last_refresh + self.__refresh_interval:
            self._client.send('FriendsTavernService', 'getOwnTavern', [])

    def _extend_tavern(self):
        # TODO implement
        pass
