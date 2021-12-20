from __future__ import annotations

import attr

from domain.city_map import CityMap
from domain.city_user_data import CityUserData
from domain.connection_state_logging import ConnectionStateLogging
from domain.hidden_reward import HiddenReward
from domain.player import Player
from domain.player_log import PlayerLog
from domain.resources import Resources
from domain.social_interaction_event import SocialInteractionEvent
from domain.socket_connection_parameter import SocketConnectionParameter
from domain.static_data import StaticData
from domain.time import Time


def map_of_hidden_rewards(list_: list[HiddenReward]) -> dict[int, HiddenReward]:
    if type(list_) == list:
        return {v.hiddenRewardId: v for v in list_}


def map_of_static_data(list_: list[StaticData]) -> dict[str, StaticData]:
    if type(list_) == list:
        return {v.identifier: v for v in list_}


def map_of_players(list_: list[Player]) -> dict[int, Player]:
    if type(list_) == list:
        return {v.player_id: v for v in list_}


def map_of_player_logs(list_: list[PlayerLog]) -> dict[int, PlayerLog]:
    if type(list_) == list:
        return {v.player_id: v for v in list_}


def map_of_social_interaction_events(list_: list[SocialInteractionEvent]) -> dict[int, SocialInteractionEvent]:
    if type(list_) == list:
        return {v.id: v for v in list_}


@attr.define
class Account:
    user_name: str = attr.ib(default=None)
    city_user_data: CityUserData = attr.attrib(default=None)
    city_map: CityMap = attr.attrib(default=None)
    socket_connection_parameter: SocketConnectionParameter = attr.attrib(default=None)
    time: Time = attr.attrib(default=None)
    connection_state_logging: ConnectionStateLogging = attr.attrib(default=None)
    resources: Resources = attr.attrib(default=None)
    hidden_rewards: dict[int, HiddenReward] = attr.attrib(default=dict[int, HiddenReward]())
    static_data: dict[str, StaticData] = attr.attrib(default=dict[str, StaticData]())
    players: dict[int, Player] = attr.attrib(default=dict[int, Player]())
    events: dict[int, SocialInteractionEvent] = attr.attrib(default=dict[int, SocialInteractionEvent]())
    player_logs: dict[int, PlayerLog] = attr.attrib(default=dict[int, PlayerLog]())

    def put_hidden_rewards(self, hidden_rewards: list[HiddenReward]) -> None:
        dict_ = map_of_hidden_rewards(hidden_rewards)
        self.hidden_rewards.update(dict_)

    def put_static_data(self, static_data: list[StaticData]) -> None:
        dict_ = map_of_static_data(static_data)
        self.static_data.update(dict_)

    def put_players(self, players: list[Player]) -> None:
        dict_ = map_of_players(players)
        if dict_:
            dict_.pop(self.city_user_data.player_id, None)
        self.players.update(dict_)

    def put_player_log(self, logs: list[PlayerLog]) -> None:
        dict_ = map_of_player_logs(logs)
        self.player_logs.update(dict_)

    def put_social_interaction_events(self, events: list[SocialInteractionEvent]) -> None:
        dict_ = map_of_social_interaction_events(events)
        self.events.update(dict_)
