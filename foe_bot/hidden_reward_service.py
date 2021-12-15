import logging
import time

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class HiddenRewardService:

    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger(self.__class__.__name__)

    def collect(self):
        now = int(time.time())
        expiry_leeway = 60
        rewards = self.__acc.hidden_rewards.values()

        filtered_rewards = [reward for reward in rewards if reward.startTime < now < reward.expireTime - expiry_leeway]

        if len(filtered_rewards) > 0:
            for reward in filtered_rewards:
                request_body = self.__request_session.create_rest_body('HiddenRewardService', 'collectReward',
                                                                       [reward.hiddenRewardId])
                response = self.__request_session.send(request_body)
                map_to_account(self.__acc, *response)

                self.__acc.hidden_rewards.pop(reward.hiddenRewardId)

            self.__logger.info(f"collected {len(filtered_rewards)} hidden reward(s)")
