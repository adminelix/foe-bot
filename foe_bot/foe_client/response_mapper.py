import json
import logging

from cattr import structure

from foe_bot.domain import SocialInteractionEvent
from foe_bot.domain.account import Account
from foe_bot.domain.city_map import CityMap
from foe_bot.domain.city_map_entity import CityMapEntity
from foe_bot.domain.city_user_data import CityUserData
from foe_bot.domain.connection_state_logging import ConnectionStateLogging
from foe_bot.domain.hidden_reward import HiddenReward
from foe_bot.domain.other_tavern_state import OtherTavernState
from foe_bot.domain.own_tavern import OwnTavern
from foe_bot.domain.player import Player
from foe_bot.domain.resources import ResourcesWrapper
from foe_bot.domain.socket_connection_parameter import SocketConnectionParameter
from foe_bot.domain.static_data import StaticData
from foe_bot.domain.tavern_config import TavernConfig
from foe_bot.domain.time import Time

__ignored = [
    'TrackingService.trackLoginDone',  # is done by login sequence via selenium webdriver
    'ResourceService.getPlayerAutoRefills',  # timestamps about last auto refilled resource, forge points for instance
    'CityMapService.relist',  # information about moppeled building when it can moppeled again
    'OtherPlayerService.rewardResources',  # resource reward of moppeled building
    'OtherPlayerService.polivateRandomBuilding',  # city_data_entity of moppeled building
    'OtherPlayerService.getAwaitingFriendRequestCount',  # amount of outstanding friend requests
    'HiddenRewardService.collectReward',  # reward collecting confirmation
    'ChatService.joinChat',  # successful join chat
    'CityMapService.reset',  # information about other player moppeled building
    'FriendService.deleteFriend',  # just player_id of deleted friend
    'RewardService.collectReward',  # reward type and amount
    'FriendsTavernService.getOtherTavern',  # details about friends tavern
    'MessageService.newMessage',  # hint that new message is available
    'ChatService.messages',  # temporary to avoid log spamming
    'ChatService.message'  # temporary to avoid log spamming
]

logger = logging.getLogger("ResponseMapper")


def __map(acc: Account, **kwargs) -> None:
    if ('StartupService' == kwargs['requestClass'] and 'getData' == kwargs['requestMethod']):
        acc.city_user_data = structure(kwargs['responseData']['user_data'], CityUserData)
        acc.city_map = structure(kwargs['responseData']['city_map'], CityMap)
        acc.socket_connection_parameter = structure(kwargs['responseData']['socket_connection_parameter'],
                                                    SocketConnectionParameter)
        acc.players = dict[int, Player]()
        acc.put_players(structure(kwargs['responseData']['socialbar_list'], list[Player]))

    elif 'TimeService' == kwargs['requestClass'] and 'updateTime' == kwargs['requestMethod']:
        acc.time = structure(kwargs['responseData'], Time)

    elif 'LogService' == kwargs['requestClass'] and kwargs['requestMethod'] in ['listLogState', 'setLogState']:
        acc.connection_state_logging = structure(kwargs['responseData'], ConnectionStateLogging)

    elif ('CityProductionService' == kwargs['requestClass']
          and kwargs['requestMethod'] in ['startProduction', 'pickupProduction', 'removePlunderedProduction']):
        acc.city_map.put_entities(structure(kwargs['responseData']['updatedEntities'], list[CityMapEntity]))

    elif 'ResourceService' == kwargs['requestClass'] and 'getPlayerResources' == kwargs['requestMethod']:
        acc.resources = structure(kwargs['responseData'], ResourcesWrapper).resources

    elif 'HiddenRewardService' == kwargs['requestClass'] and 'getOverview' == kwargs['requestMethod']:
        acc.put_hidden_rewards(structure(kwargs['responseData']['hiddenRewards'], list[HiddenReward]))

    elif 'StaticDataService' == kwargs['requestClass'] and 'getMetadata' == kwargs['requestMethod']:
        acc.put_static_data(structure(kwargs['responseData'], list[StaticData]))

    elif ('OtherPlayerService' == kwargs['requestClass']
          and kwargs['requestMethod'] in ['updatePlayer', 'getFriendsList', 'getNeighborList', 'getClanMemberList']):
        acc.put_players(structure(kwargs['responseData'], list[Player]))

    elif ('FriendService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'acceptInvitation'):
        if type(kwargs['responseData']) == list:
            acc.put_players(structure(kwargs['responseData'], list[Player]))
        else:
            acc.put_players([structure(kwargs['responseData'], Player)])

    elif ('FriendService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'invitePlayerById'):
        acc.put_players([structure(kwargs['responseData'], Player)])

    elif ('OtherPlayerService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'getEventsPaginated'):
        # TODO consider towerRankings ?
        event_ids = acc.events.keys()
        events = [event for event in kwargs['responseData']['events'] if event['id'] not in event_ids]
        acc.put_social_interaction_events(structure(events, list[SocialInteractionEvent]))

    elif ('OtherPlayerService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'newEvent'):
        acc.put_social_interaction_events([structure(kwargs['responseData'], SocialInteractionEvent)])

    elif ('FriendsTavernService' == kwargs['requestClass']
          and kwargs['requestMethod'] in ['getOtherTavernStates', 'getOtherTavernState', 'receiveInvite']):
        if type(kwargs['responseData']) == list:
            acc.put_other_tavern_states(structure(kwargs['responseData'], list[OtherTavernState]))
        else:
            acc.put_other_tavern_states([structure(kwargs['responseData'], OtherTavernState)])

    elif ('FriendsTavernService' == kwargs['requestClass']
          and kwargs['requestMethod'] in ['getOwnTavern', 'unlockChair', 'upgradeTable', 'unlockCustomization']):
        acc.own_tavern = structure(kwargs['responseData'], OwnTavern)

    elif ('FriendsTavernService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'getSittingPlayersCount'):
        state = acc.other_tavern_states.get(kwargs['responseData'][0], OtherTavernState(kwargs['responseData'][0]))
        state.unlockedChairCount = kwargs['responseData'][1]
        state.sittingPlayerCount = kwargs['responseData'][2]
        acc.put_other_tavern_states([state])

    elif ('CityMapService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'updateEntity'):
        if type(kwargs['responseData']) == list:
            acc.city_map.put_entities(structure(kwargs['responseData'], list[CityMapEntity]))
        else:
            acc.city_map.put_entities([structure(kwargs['responseData'], CityMapEntity)])

    elif ('FriendsTavernService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'getConfig'):
        acc.tavern_config = structure(kwargs['responseData'], TavernConfig)

    else:
        class_method = f"{kwargs['requestClass']}.{kwargs['requestMethod']}"
        if class_method not in __ignored:
            logger.info(f"no mapping for {class_method}: '{json.dumps(kwargs)}'")


def map_to_account(acc: Account, *args) -> Account:
    for arg in args:
        try:
            __map(acc, **arg)
        except Exception as e:
            logger.exception(f"cannot map '{arg}'", e)
    return acc
