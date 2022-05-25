import json
import logging
from concurrent.futures import ThreadPoolExecutor, wait

from foe_bot.domain import structure
from foe_bot.domain.account import Account
from foe_bot.domain.city_map import CityMap
from foe_bot.domain.city_map_entity import CityMapEntity
from foe_bot.domain.city_user_data import CityUserData
from foe_bot.domain.connection_state_logging import ConnectionStateLogging
from foe_bot.domain.hidden_reward import HiddenReward
from foe_bot.domain.inventory_item import InventoryItem
from foe_bot.domain.other_tavern_state import OtherTavernState
from foe_bot.domain.own_tavern import OwnTavern
from foe_bot.domain.player import Player
from foe_bot.domain.resources import ResourcesWrapper
from foe_bot.domain.social_interaction_event import SocialInteractionEvent
from foe_bot.domain.socket_connection_parameter import SocketConnectionParameter
from foe_bot.domain.static_data import StaticData
from foe_bot.domain.tavern_config import TavernConfig
from foe_bot.domain.time import Time

__ignored = [
    'TrackingService.trackLoginDone',  # is done by login sequence via selenium webdriver
    'ResourceService.getPlayerAutoRefills',  # timestamps about last auto refilled resource, forge points for instance
    'ResourceService.getResourceDefinitions',  # timestamps about last auto refilled resource, forge points for instance
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
    'FriendsTavernService.collectReward',  # empty confirmation message
    'MessageService.newMessage',  # hint that new message is available
    'ChatService.messages',  # temporary to avoid log spamming
    'ChatService.message',  # temporary to avoid log spamming
    'GreatBuildingsService.getOtherPlayerOverview',  # temporary to avoid log spamming
    'GreatBuildingsService.getConstruction',  # temporary to avoid log spamming
    'GreatBuildingsService.contributeForgePoints',  # temporary to avoid log spamming
    'BonusService.getBonuses',  # temporary to avoid log spamming
    'BoostService.getAllBoosts',  # temporary to avoid log spamming
    'CrmService.getContent',  # temporary to avoid log spamming
    'CampaignService.getDeposits',  # temporary to avoid log spamming
    'CastleSystemService.getCastleSystemPlayer',  # temporary to avoid log spamming
    'CastleSystemService.getOverview',  # temporary to avoid log spamming
    'ChallengeService.getActiveChallenges',  # temporary to avoid log spamming
    'ChallengeService.getOptions',  # temporary to avoid log spamming
    'CityMapService.getNextId',  # temporary to avoid log spamming
    'ResourceService.getResourceDefinition',  # temporary to avoid log spamming
    'ForgePlusPackageService.getPackages',  # temporary to avoid log spamming
    'FriendService.getInvitationLink',  # temporary to avoid log spamming
    'BonusService.getLimitedBonuses',  # temporary to avoid log spamming
    'ItemExchangeService.getConfig',  # temporary to avoid log spamming
    'ItemShopService.getOffers',  # temporary to avoid log spamming
    'OutpostService.getAll',  # temporary to avoid log spamming
    'EmissaryService.getAssigned',  # temporary to avoid log spamming
    'PremiumService.getActiveBundle',  # temporary to avoid log spamming
    'SaleInfoService.getActiveSales',  # temporary to avoid log spamming
    'IgnorePlayerService.getIgnoreList',  # temporary to avoid log spamming
    'PlayerProfileService.getFreeNameChangeTime',  # temporary to avoid log spamming
    'NoticeIndicatorService.getPlayerNoticeIndicators',  # temporary to avoid log spamming
    'RankingService.newRank',  # temporary to avoid log spamming
    'ResearchService.getProgress',  # temporary to avoid log spamming
    'OtherPlayerService.updateActions',  # FIXME temporary to avoid log spamming
    'OtherPlayerService.getSocialList',  # FIXME temporary to avoid log spamming
    'OtherPlayerService.getCityProtections',  # temporary to avoid log spamming
    'TimerService.getTimers',  # temporary to avoid log spamming
    'TutorialService.getProgress',  # temporary to avoid log spamming
    'QuestService.getUpdates',  # temporary to avoid log spamming
    'AnnouncementsService.fetchAllAnnouncements',  # temporary to avoid log spamming
    'CashShopService.getPricingInformation',  # temporary to avoid log spamming
    'ConversationService.getUpdatedMessage',  # temporary to avoid log spamming
    'ConversationService.getNewMessage',  # temporary to avoid log spamming
    'ConversationService.getConversationUpdate',  # temporary to avoid log spamming
    'BlueprintService.getUpdates',  # temporary to avoid log spamming
    'PremiumService.getActivePackages',  # temporary to avoid log spamming
    'InventoryService.getItemAmount',  # temporary to avoid log spamming
    'RankingService.searchRanking',  # temporary to avoid log spamming
    'OneTimeNotificationService.getPayloadForIds',  # temporary to avoid log spamming
    'GuildExpeditionNotificationService.getNotification',  # temporary to avoid log spamming
    'OneTimeNotificationService.getIds',  # temporary to avoid log spamming
    'InventoryService.getGreatBuildings'  # temporary to avoid log spamming
]

logger = logging.getLogger("ResponseMapper")


def __map(acc: Account, **kwargs) -> None:
    if ('StartupService' == kwargs['requestClass'] and 'getData' == kwargs['requestMethod']):
        acc.city_user_data = structure(kwargs['responseData']['user_data'], CityUserData)
        acc.city_map = structure(kwargs['responseData']['city_map'], CityMap)
        acc.socket_connection_parameter = structure(kwargs['responseData']['socket_connection_parameter'],
                                                    SocketConnectionParameter)
        acc.players = dict[int, Player]()
        if kwargs['responseData'].get('socialbar_list'):
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
        filtered = [event for event in kwargs['responseData']['events'] if event['id'] not in event_ids]

        with ThreadPoolExecutor(20) as executor:
            futures = [executor.submit(structure, event, SocialInteractionEvent) for event in filtered]
            wait(futures)
            events = [future.result() for future in futures]

        acc.put_social_interaction_events(events)

    elif ('OtherPlayerService' == kwargs['requestClass']
          and 'newEvent' in kwargs['requestMethod']
          and 'MessageEvent' not in kwargs['responseData']['klass']):
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
            entities = structure(kwargs['responseData'], list[CityMapEntity])
            entities = [entity for entity in entities if entity.player_id == acc.city_user_data.player_id]
            if entities:
                acc.city_map.put_entities(entities)
        else:
            entity = [structure(kwargs['responseData'], CityMapEntity)]
            if entity[0].player_id == acc.city_user_data.player_id:
                acc.city_map.put_entities(entity)

    elif ('FriendsTavernService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'getConfig'):
        acc.tavern_config = structure(kwargs['responseData'], TavernConfig)

    elif ('InventoryService' == kwargs['requestClass']
          and kwargs['requestMethod'] == 'getItems'):
        if type(kwargs['responseData']) == list:
            acc.put_inventory_items(structure(kwargs['responseData'], list[InventoryItem]))
        else:
            acc.put_inventory_items([structure(kwargs['responseData'], InventoryItem)])

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
