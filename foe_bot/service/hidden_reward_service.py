import logging
import time

from foe_bot.service.abstract_service import AbstractService


class HiddenRewardService(AbstractService):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)

    def do(self):
        self._collect()

    def _collect(self):
        now = int(time.time())
        expiry_leeway = 60
        rewards = self._acc.hidden_rewards.values()

        filtered_rewards = [reward for reward in rewards if reward.startTime < now < reward.expireTime - expiry_leeway]

        counter = 0
        if len(filtered_rewards) > 0:
            for reward in filtered_rewards:
                success = self._client.send('HiddenRewardService', 'collectReward', [reward.hiddenRewardId])
                self._acc.hidden_rewards.pop(reward.hiddenRewardId)

                if success:
                    counter += 1

        if counter > 0:
            self.__logger.info(f"collected {counter} hidden reward(s)")
