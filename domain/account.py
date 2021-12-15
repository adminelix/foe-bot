from __future__ import annotations

import attr

from domain.city_map import CityMap
from domain.city_user_data import CityUserData
from domain.connection_state_logging import ConnectionStateLogging
from domain.hidden_reward import HiddenReward
from domain.resources import Resources
from domain.socket_connection_parameter import SocketConnectionParameter
from domain.time import Time


@attr.s(init=False)
class Account:
    user_name: str
    city_user_data: CityUserData = CityUserData()
    city_map: CityMap = CityMap()
    socket_connection_parameter: SocketConnectionParameter = SocketConnectionParameter()
    time: Time = Time()
    connection_state_logging: ConnectionStateLogging = ConnectionStateLogging()
    resources = Resources()
    hidden_rewards: dict[int, HiddenReward] = {}

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def put_hidden_rewards(self, *args) -> None:
        for arg in args:
            hidden_reward = HiddenReward(**arg)
            self.hidden_rewards[hidden_reward.hiddenRewardId] = hidden_reward
