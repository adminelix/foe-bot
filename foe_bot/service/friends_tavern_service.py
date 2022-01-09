import logging
import time

from foe_bot import cfg
from foe_bot.service.abstract_service import AbstractService


class FriendsTavernService(AbstractService):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__config = cfg.get('friends_tavern_service')
        self.__last_refresh = 0
        self.__refresh_interval = 15 * 60  # in seconds
        self.__budget_factor: float = 0.1
        self.__min_chairs = 6
        self.__refresh_own_tavern(False)

    def do(self) -> None:
        # FIXME check if tavern is unlocked
        self._collect()
        self._visit()
        self._get_config()
        if self.__config.get('upgrade', None):
            self._extend_tavern()

    def _collect(self) -> None:
        own_tavern_state = self._acc.other_tavern_states.get(self._acc.city_user_data.player_id, None)

        if own_tavern_state and own_tavern_state.unlockedChairCount == own_tavern_state.sittingPlayerCount:
            success = self._client.send('FriendsTavernService', 'collectReward', [])

            if success:
                self.__logger.info("collected tavern rewards")

            self.__refresh_own_tavern(True)

    def _visit(self) -> None:
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

    def _get_config(self) -> None:
        if not self._acc.tavern_config:
            self._client.send('FriendsTavernService', 'getConfig', [])

    def _extend_tavern(self) -> None:
        self.__refresh_own_tavern(False)
        table_level = self._acc.own_tavern.view.tableLevel
        unlocked_chairs = self._acc.own_tavern.view.unlockedChairs

        self.__unlock_chair(table_level, unlocked_chairs)
        self.__unlock_table(table_level, unlocked_chairs)
        self.__unlock_customization()

    def __unlock_table(self, table_level, unlocked_chairs) -> None:
        table_unlockable = (unlocked_chairs == self.__min_chairs + table_level * 2
                            and table_level != len(self._acc.tavern_config.tableUnlockCosts))

        if table_unlockable:
            tavern_silver_costs = self._acc.tavern_config.tableUnlockCosts[
                table_level].normalCosts.resources.tavern_silver

            if tavern_silver_costs < self._acc.resources.tavern_silver * self.__budget_factor:
                success = self._client.send('FriendsTavernService', 'upgradeTable', [False])
                if success:
                    self.__logger.info(f"unlocked table level {self._acc.own_tavern.view.tableLevel}")

    def __unlock_chair(self, table_level, unlocked_chairs) -> None:
        chair_unlockable = (unlocked_chairs < self.__min_chairs + table_level * 2
                            and unlocked_chairs != len(self._acc.tavern_config.chairUnlockCosts))

        if chair_unlockable:
            tavern_silver_costs = self._acc.tavern_config.chairUnlockCosts[
                unlocked_chairs - 1].normalCosts.resources.tavern_silver

            if tavern_silver_costs < self._acc.resources.tavern_silver * self.__budget_factor:
                success = self._client.send('FriendsTavernService', 'unlockChair', [False])
                if success:
                    self.__logger.info(f"unlocked chair {self._acc.own_tavern.view.unlockedChairs}")

    def __unlock_customization(self) -> None:
        unlocked_customizations = self._acc.own_tavern.unlockedCustomizationIds
        unlockable_customizations = [customization for customization in self._acc.tavern_config.customizations if
                                     customization.id not in unlocked_customizations
                                     and set(customization.requiredCustomizationIds).issubset(unlocked_customizations)]

        for customization in unlockable_customizations:
            tavern_silver_costs = customization.unlockCosts.normalCosts.resources.tavern_silver
            if tavern_silver_costs < self._acc.resources.tavern_silver * self.__budget_factor:
                success = self._client.send('FriendsTavernService', 'unlockCustomization', [customization.id, False])
                if success:
                    self.__logger.info(f"unlocked customization '{customization.name}'")

    def __refresh_own_tavern(self, force: bool) -> None:
        now = int(time.time())
        if force or now > self.__last_refresh + self.__refresh_interval:
            self._client.send('FriendsTavernService', 'getOwnTavern', [])
            self.__last_refresh = now
            self.__logger.info("refreshed tavern")
