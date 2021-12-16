from __future__ import annotations

import attr

from domain.city_map import CityMap
from domain.city_user_data import CityUserData
from domain.connection_state_logging import ConnectionStateLogging
from domain.hidden_reward import HiddenReward
from domain.player import Player
from domain.resources import Resources
from domain.socket_connection_parameter import SocketConnectionParameter
from domain.static_data import StaticData
from domain.time import Time

# TODO improve domain model (de)-serialization with cattr https://cattrs.readthedocs.io/en/latest/readme.html
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
    static_data: dict[str, StaticData] = {}
    player: dict[int, Player] = {}

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def put_hidden_rewards(self, *args) -> None:
        for arg in args:
            hidden_reward = HiddenReward(**arg)
            self.hidden_rewards[hidden_reward.hiddenRewardId] = hidden_reward

    def put_static_data(self, *args) -> None:
        for arg in args:
            static_data = StaticData(**arg)
            self.static_data[static_data.identifier] = static_data

    def put_player(self, *args) -> None:
        for arg in args:
            player = Player(**arg)
            if player.player_id == self.city_user_data.player_id:
                continue
            self.player[player.player_id] = player
