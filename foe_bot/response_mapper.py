import logging

from cattr import structure

from domain.account import Account
from domain.city_map import CityMap
from domain.city_map_entity import CityMapEntity
from domain.city_user_data import CityUserData
from domain.connection_state_logging import ConnectionStateLogging
from domain.hidden_reward import HiddenReward
from domain.player import Player
from domain.resources import Resources, ResourcesWrapper
from domain.socket_connection_parameter import SocketConnectionParameter
from domain.static_data import StaticData
from domain.time import Time

__ignored = [
    'TrackingService.trackLoginDone',  # is done by login sequence via selenium webdriver
    'ResourceService.getPlayerAutoRefills',  # timestamps about last auto refilled resource, forge points for instance
    'ChatService.messages',  # chat messages that come mostly from websocket
    'CityMapService.relist',  # information about moppeled building when it can moppeled again
    'OtherPlayerService.rewardResources',  # resource reward of moppeled building
    'OtherPlayerService.polivateRandomBuilding',  # city_data_entity of moppeled building
    'OtherPlayerService.getAwaitingFriendRequestCount'  # amount of outstanding friend requests
]

logger = logging.getLogger("ResponseMapper")


def __map(acc: Account, **kwargs) -> None:
    if ('StartupService' == kwargs['requestClass'] and 'getData' == kwargs['requestMethod']):
        acc.city_user_data = structure(kwargs['responseData']['user_data'], CityUserData)
        acc.city_map = structure(kwargs['responseData']['city_map'], CityMap)
        acc.socket_connection_parameter = structure(kwargs['responseData']['socket_connection_parameter'],
                                                    SocketConnectionParameter)

        acc.put_players(structure(kwargs['responseData']['socialbar_list'], list[Player]))

    elif 'TimeService' == kwargs['requestClass'] and 'updateTime' == kwargs['requestMethod']:
        acc.time = structure(kwargs['responseData'], Time)

    elif 'LogService' == kwargs['requestClass'] and 'listLogState' == kwargs['requestMethod']:
        acc.connection_state_logging = structure(kwargs['responseData'], ConnectionStateLogging)

    elif ('CityProductionService' == kwargs['requestClass']
          and ('startProduction' == kwargs['requestMethod']
               or 'pickupProduction' == kwargs['requestMethod'])):
        l = structure(kwargs['responseData']['updatedEntities'], list[CityMapEntity])
        acc.city_map.put_entities(l)

    elif 'ResourceService' == kwargs['requestClass'] and 'getPlayerResources' == kwargs['requestMethod']:
        acc.resources = structure(kwargs['responseData'], ResourcesWrapper).resources

    elif 'HiddenRewardService' == kwargs['requestClass'] and 'getOverview' == kwargs['requestMethod']:
        acc.put_hidden_rewards(structure(kwargs['responseData']['hiddenRewards'], list[HiddenReward]))

    elif 'StaticDataService' == kwargs['requestClass'] and 'getMetadata' == kwargs['requestMethod']:
        acc.put_static_data(structure(kwargs['responseData'], list[StaticData]))

    elif ('OtherPlayerService' == kwargs['requestClass']
          and kwargs['requestMethod'] in ['updatePlayer', 'getFriendsList', 'getNeighborList', 'getClanMemberList']):
        acc.put_player(structure(kwargs['responseData'], list[Player]))

    else:
        class_method = f"{kwargs['requestClass']}.{kwargs['requestMethod']}"
        if class_method not in __ignored:
            logger.info(f"no mapping for {class_method}")


def map_to_account(acc: Account, *args) -> Account:
    for arg in args:
        __map(acc, **arg)
    return acc
