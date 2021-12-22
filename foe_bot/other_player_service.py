import json
import logging
import time

from domain.account import Account
from domain.player import Player
from domain.player_log import PlayerLog
from foe_bot import cfg
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class OtherPlayerService:

    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__last_refresh = 0
        self.__refresh_interval = 15 * 60  # in seconds
        self.__config = cfg.get('other_player_service')

    def moppel(self):
        if not self.__config.get('moppel', None):
            return
        self.__refresh_player()
        player_map = self.__acc.players
        player_to_moppel = [player for (key, player) in player_map.items()
                            if not player.next_interaction_in and not player.isInvitedFriend]

        for player in player_to_moppel:
            body = self.__request_session.create_rest_body('OtherPlayerService', 'polivateRandomBuilding',
                                                           [player.player_id])
            response, _ = self.__request_session.send(body)
            map_to_account(self.__acc, *response)

        if len(player_to_moppel) > 0:
            self.__logger.info(f"moppeled {len(player_to_moppel)} player")

    def accept_friend_invites(self):
        if not self.__config.get('manage_friends', None):
            return
        player_map = self.__acc.players
        max_friends = 140
        friends_amount = len([player for (key, player) in player_map.items() if player.is_friend])

        if friends_amount < max_friends:
            player_to_accept = [player for (key, player) in player_map.items()
                                if player.isInvitedFriend and player.incoming and not player.accepted]

            for player in player_to_accept:
                body = self.__request_session.create_rest_body('FriendService', 'acceptInvitation', [player.player_id])
                response, _ = self.__request_session.send(body)
                map_to_account(self.__acc, *response)
                self.__logger.info(f"accept friend invite from {player.name}")

    def send_friend_invites(self):
        if not self.__config.get('manage_friends', None):
            return
        now = int(time.time())
        player_map = self.__acc.players
        player_logs = self.__acc.player_logs
        max_friends = 79
        friends_amount = len([player for (key, player) in player_map.items() if player.is_friend])
        free_slots = max_friends - friends_amount

        if friends_amount < max_friends:
            player_to_invite = self._filter_players_to_invite(now, player_logs, player_map)

            for player in player_to_invite:
                body = self.__request_session.create_rest_body('FriendService', 'invitePlayerById', [player.player_id])
                response, successful = self.__request_session.send(body)
                log = player_logs.get(player.player_id, PlayerLog(player.player_id))
                if successful:
                    map_to_account(self.__acc, *response)
                    log.invited_at = int(time.time())
                    self.__logger.info(f"send friend invite to '{player.name}'")
                    free_slots -= 1

                log.invite_blocked_until = int(time.time()) * (60 * 60 * 24 * 30)
                self.__acc.put_player_log([log])
                if free_slots < 1:
                    break

    def revoke_friend_invites(self):
        if not self.__config.get('manage_friends', None):
            return
        now = int(time.time())
        player_to_revoke = self._filter_player_with_expired_friends_invite(now)

        for player in player_to_revoke:
            body = self.__request_session.create_rest_body('FriendService', 'deleteFriend', [player.player_id])
            response, successful = self.__request_session.send(body)
            if successful:
                map_to_account(self.__acc, *response)
                self.__acc.players.get(player.player_id).isInvitedFriend = False
                player_log = self.__acc.player_logs.get(player.player_id, PlayerLog(player.player_id))
                player_log.invited_at = -1
                player_log.invite_blocked_until = now + (60 * 60 * 24 * 30)
                self.__acc.put_player_log([player_log])
                self.__logger.info(f"revoke friends invite to '{player.name}'")

    def remove_useless_friends(self):
        if not self.__config.get('manage_friends', None):
            return
        now = int(time.time())

        useless_friends = self._filter_useless_friends(now)

        for player in useless_friends:
            body = self.__request_session.create_rest_body('FriendService', 'deleteFriend', [player.player_id])
            response, successful = self.__request_session.send(body)
            if successful:
                map_to_account(self.__acc, *response)
                self.__acc.players.get(player.player_id).is_friend = False
                player_log = self.__acc.player_logs.get(player.player_id, PlayerLog(player.player_id))
                player_log.invited_at = -1
                player_log.invite_blocked_until = now + (60 * 60 * 24 * 30)
                self.__acc.put_player_log([player_log])
                self.__logger.info(f"removed friend '{player.name}'")

    def get_events(self):
        last_event_time: int = 0
        events = self.__acc.events
        for event in events.values():
            last_event_time = event.date if event.date > last_event_time else last_event_time

        one_day_ago = int(time.time()) - (60 * 60 * 24 * 3)
        if last_event_time < one_day_ago:
            raw_body = json.loads("""
            {
                 "__class__": "EventHistoryRequest",
                 "getAll": true,
                 "countTotalEvents": true,
                 "page": 1,
                 "amountPerPage": 10,
                 "getTowerRanking": true
             }
            """)

            body = self.__request_session.create_rest_body('OtherPlayerService', 'getEventsPaginated', [raw_body])
            response, _ = self.__request_session.send(body)

            event_ids = self.__acc.events.keys()
            response_data_index = [x for x in range(len(response)) if 'getEventsPaginated' in response[x].values()][0]
            filtered_events = [event for event in response[response_data_index]['responseData']['events'] if
                               event['id'] not in event_ids]
            response[response_data_index]['responseData']['events'] = filtered_events

            map_to_account(self.__acc, *response)
            self.__logger.info(f"got {len(filtered_events)} new events")

    def _filter_players_to_invite(self, now, player_logs, player_map):
        player_to_invite = [player for (key, player) in player_map.items()
                            if not player.isInvitedFriend
                            and not player.is_friend
                            and player.is_active
                            and player_logs.get(player.player_id,
                                                PlayerLog(player.player_id)).invite_blocked_until < now]
        return player_to_invite

    def _filter_player_with_expired_friends_invite(self, now: int) -> list[Player]:
        before_7_days = now - (60 * 60 * 24 * 7)
        player_map = self.__acc.players
        player_logs = self.__acc.player_logs
        player_to_revoke = [player for player in player_map.values()
                            if player.isInvitedFriend
                            and not player.is_friend
                            and player_logs.get(player.player_id,
                                                PlayerLog(player.player_id)).invited_at < before_7_days]
        return player_to_revoke

    def _filter_useless_friends(self, now: int) -> list[Player]:
        before_7_days = now - (60 * 60 * 24 * 7)
        player_map = self.__acc.players
        events = self.__acc.events
        friends = {key: player for (key, player) in player_map.items() if player.is_friend}
        moppeling_player_ids = set([event.other_player.player_id for event in events.values()
                                    if event.date > before_7_days
                                    and (event.interaction_type in ['motivate', 'polish']
                                         or 'friend_tavern_sat_down' in event.type)])
        fresh_friendships = set([event.other_player.name for event in events.values() if
                                 event.type == 'friend_accepted' and event.date > before_7_days])
        useless_friends = [player for player in friends.values() if
                           player.player_id not in moppeling_player_ids and player.player_id not in fresh_friendships]
        return useless_friends

    def __refresh_player(self):
        now = int(time.time())
        if self.__last_refresh + self.__refresh_interval < now:
            self.__refresh_neighbor_list()  # must be refreshed at first because does not include all data about player
            self.__refresh_friend_list()  # overwrites object if friend is neighbor with more attributes
            self.__refresh_clan_member_list()
            self.__last_refresh = now

            self.__logger.info(f"players refreshed")

    def __refresh_neighbor_list(self):
        body = self.__request_session.create_rest_body('OtherPlayerService', 'getNeighborList', [])
        response, _ = self.__request_session.send(body)
        map_to_account(self.__acc, *response)

    def __refresh_friend_list(self):
        body = self.__request_session.create_rest_body('OtherPlayerService', 'getFriendsList', [])
        response, _ = self.__request_session.send(body)
        map_to_account(self.__acc, *response)

    def __refresh_clan_member_list(self):
        if len(self.__acc.city_user_data.clan_name) > 0:
            body = self.__request_session.create_rest_body('OtherPlayerService', 'getClanMemberList', [])
            response, _ = self.__request_session.send(body)
            map_to_account(self.__acc, *response)


# {
#     "__class__": "ServerRequest",
#     "requestData": [],
#     "requestClass": "OtherPlayerService",
#     "requestMethod": "getNeighborList",
#     "requestId": 14
# }

# {
#     "__class__": "ServerRequest",
#     "requestData": [],
#     "requestClass": "OtherPlayerService",
#     "requestMethod": "getFriendsList",
#     "requestId": 15
# }

# {
#     "__class__": "ServerRequest",
#     "requestData": [],
#     "requestClass": "ClanRecruitmentService",
#     "requestMethod": "getJoinableClans",
#     "requestId": 18
# }

# {
#     "__class__": "ServerRequest",
#     "requestData": [],
#     "requestClass": "OtherPlayerService",
#     "requestMethod": "getClanMemberList",
#     "requestId": 17
# }

# {
#     "__class__": "ServerRequest",
#     "requestData": [
#         9965783
#     ],
#     "requestClass": "FriendService",
#     "requestMethod": "acceptInvitation",
#     "requestId": 16
# }

# [
#     {
#         "__class__": "ServerRequest",
#         "requestData": [
#             850894960
#         ],
#         "requestClass": "FriendService",
#         "requestMethod": "invitePlayerById",
#         "requestId": 25
#     }
# ]

# [
#     {
#         "__class__": "ServerRequest",
#         "requestData": [],
#         "requestClass": "FriendService",
#         "requestMethod": "getFriendSuggestions",
#         "requestId": 27
#     }
# ]

# [
#     {
#         "responseData": [
#             {
#                 "score": 977362195,
#                 "rank": 1,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 3780,
#                 "canSabotage": false,
#                 "era": "SpaceAgeVenus",
#                 "showAvatarFrame": false,
#                 "player_id": 9947792,
#                 "name": "Kultbaer",
#                 "avatar": "addon_portrait_id_castle_system_jasib",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 155989237,
#                 "rank": 2,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 392,
#                 "canSabotage": false,
#                 "era": "ArcticFuture",
#                 "showAvatarFrame": false,
#                 "player_id": 7067692,
#                 "name": "Master Boy",
#                 "avatar": "portrait_id_145",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 27918969,
#                 "rank": 3,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 7296,
#                 "canSabotage": false,
#                 "era": "PostModernEra",
#                 "showAvatarFrame": false,
#                 "player_id": 10246265,
#                 "name": "MCFE",
#                 "avatar": "portrait_id_49",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 15508709,
#                 "rank": 4,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 1276,
#                 "canSabotage": false,
#                 "era": "ProgressiveEra",
#                 "showAvatarFrame": false,
#                 "player_id": 5487637,
#                 "name": "SigridAnna",
#                 "avatar": "portrait_id_35",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 9161467,
#                 "rank": 5,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 11074,
#                 "canSabotage": false,
#                 "era": "ProgressiveEra",
#                 "showAvatarFrame": false,
#                 "player_id": 10212064,
#                 "name": "Myarah",
#                 "avatar": "portrait_id_35",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 8845391,
#                 "rank": 6,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 6719,
#                 "canSabotage": false,
#                 "era": "HighMiddleAge",
#                 "showAvatarFrame": false,
#                 "player_id": 849427238,
#                 "name": "löschfix",
#                 "avatar": "portrait_id_99",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 7357941,
#                 "rank": 7,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 19231,
#                 "canSabotage": false,
#                 "era": "ProgressiveEra",
#                 "showAvatarFrame": false,
#                 "player_id": 10128713,
#                 "name": "Hecki 40625",
#                 "avatar": "addon_portrait_id_pirate_king",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 4879359,
#                 "rank": 8,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "canSabotage": false,
#                 "era": "FutureEra",
#                 "showAvatarFrame": false,
#                 "player_id": 10055402,
#                 "name": "Powerranger",
#                 "avatar": "addon_portrait_id_napoleon",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 3933696,
#                 "rank": 9,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 4676,
#                 "canSabotage": false,
#                 "era": "ArcticFuture",
#                 "showAvatarFrame": false,
#                 "player_id": 9456263,
#                 "name": "diver66",
#                 "avatar": "portrait_id_20",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 1172317,
#                 "rank": 10,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 5997,
#                 "canSabotage": false,
#                 "era": "PostModernEra",
#                 "showAvatarFrame": false,
#                 "player_id": 7233490,
#                 "name": "schuermd",
#                 "avatar": "portrait_id_100",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 31163,
#                 "rank": 11,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "canSabotage": false,
#                 "era": "LateMiddleAge",
#                 "showAvatarFrame": false,
#                 "player_id": 850638853,
#                 "name": "Lupus Lupus",
#                 "avatar": "portrait_id_13",
#                 "__class__": "Player"
#             },
#             {
#                 "score": 7700,
#                 "rank": 12,
#                 "is_friend": false,
#                 "isInvitedToClan": false,
#                 "isInvitedFriend": false,
#                 "clan_id": 7954,
#                 "canSabotage": false,
#                 "era": "EarlyMiddleAge",
#                 "showAvatarFrame": false,
#                 "player_id": 850728096,
#                 "name": "Nics Paradise",
#                 "avatar": "portrait_id_4",
#                 "__class__": "Player"
#             }
#         ],
#         "requestClass": "FriendService",
#         "requestMethod": "getFriendSuggestions",
#         "requestId": 28,
#         "__class__": "ServerResponse"
#     }
# ]

# get event history
# [
#     {
#         "__class__": "ServerRequest",
#         "requestData": [
#             {
#                 "__class__": "EventHistoryRequest",
#                 "getAll": false,
#                 "countTotalEvents": true,
#                 "page": 1,
#                 "amountPerPage": 10,
#                 "getTowerRanking": true
#             }
#         ],
#         "requestClass": "OtherPlayerService",
#         "requestMethod": "getEventsPaginated",
#         "requestId": 35
#     }
# ]

# [
#     {
#         "responseData": {
#             "page": 1,
#             "events": [
#                 {
#                     "interaction_type": "motivate",
#                     "entity_id": "R_BronzeAge_Residential4",
#                     "id": 139628066,
#                     "player_id": 8365227,
#                     "date": "heute um 18:02 Uhr",
#                     "other_player": {
#                         "is_friend": true,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48536,
#                         "city_name": "Trinkerrrs Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 9965783,
#                         "name": "NeoXymor",
#                         "avatar": "portrait_id_16",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "polish",
#                     "entity_id": "D_StoneAge_Tree",
#                     "id": 139469932,
#                     "player_id": 8365227,
#                     "date": "heute um 13:37 Uhr",
#                     "other_player": {
#                         "is_friend": true,
#                         "is_neighbor": false,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48580,
#                         "city_name": "Old Foxis Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850894960,
#                         "name": "Old Foxi",
#                         "avatar": "addon_portrait_id_castle_system_anselm",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "polish",
#                     "entity_id": "A_BronzeAge_Memorial",
#                     "id": 139436798,
#                     "player_id": 8365227,
#                     "date": "heute um 12:50 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48535,
#                         "city_name": "Illidas Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850763818,
#                         "name": "Illida",
#                         "avatar": "portrait_id_9",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "motivate",
#                     "entity_id": "R_BronzeAge_Residential4",
#                     "id": 139423934,
#                     "player_id": 8365227,
#                     "date": "heute um 12:26 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48539,
#                         "city_name": "new pentagons Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850884095,
#                         "name": "new pentagon",
#                         "avatar": "portrait_id_4",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "motivate",
#                     "entity_id": "R_BronzeAge_Residential4",
#                     "id": 139347006,
#                     "player_id": 8365227,
#                     "date": "heute um 10:27 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48541,
#                         "city_name": "Notans Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 849825925,
#                         "name": "Notan",
#                         "avatar": "portrait_id_26",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "motivate",
#                     "entity_id": "R_BronzeAge_Residential4",
#                     "id": 139314665,
#                     "player_id": 8365227,
#                     "date": "heute um 09:44 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48559,
#                         "city_name": "max von kaltenborns Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850781668,
#                         "name": "max von kaltenborn",
#                         "avatar": "portrait_id_22",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "polish",
#                     "entity_id": "D_StoneAge_Statue",
#                     "id": 139236810,
#                     "player_id": 8365227,
#                     "date": "heute um 08:13 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48543,
#                         "city_name": "Jornes Stadt O",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850894902,
#                         "name": "Jorne",
#                         "avatar": "portrait_id_6",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "motivate",
#                     "entity_id": "R_BronzeAge_Residential4",
#                     "id": 139211822,
#                     "player_id": 8365227,
#                     "date": "heute um 07:35 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48536,
#                         "city_name": "Dorfchemnitz",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850870657,
#                         "name": "Caedmon",
#                         "avatar": "portrait_id_125",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "polish",
#                     "entity_id": "D_StoneAge_Tree",
#                     "id": 139152516,
#                     "player_id": 8365227,
#                     "date": "heute um 05:28 Uhr",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48539,
#                         "city_name": "Eurichs Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850888608,
#                         "name": "Eurich 858 der Pfähler",
#                         "avatar": "portrait_id_118",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 },
#                 {
#                     "interaction_type": "polish",
#                     "entity_id": "D_StoneAge_Tree",
#                     "id": 139097923,
#                     "player_id": 8365227,
#                     "date": "gestern um 23:56",
#                     "other_player": {
#                         "is_friend": false,
#                         "is_neighbor": true,
#                         "is_guild_member": false,
#                         "next_interaction_in": 48550,
#                         "city_name": "Tuna1453s Stadt",
#                         "is_active": true,
#                         "canSabotage": false,
#                         "showAvatarFrame": false,
#                         "player_id": 850899916,
#                         "name": "Tuna1453",
#                         "avatar": "portrait_id_8",
#                         "__class__": "OtherPlayer"
#                     },
#                     "type": "social_interaction",
#                     "__class__": "SocialInteractionEvent"
#                 }
#             ],
#             "totalEvents": 58,
#             "amountPerPage": 10,
#             "towerRankings": [
#                 [
#                     {
#                         "time_remaining": 189002,
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "BronzeAge",
#                         "place": 16,
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "IronAge",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "EarlyMiddleAge",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "HighMiddleAge",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "LateMiddleAge",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "ColonialAge",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "IndustrialAge",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "ProgressiveEra",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "ModernEra",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "PostModernEra",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "ContemporaryEra",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "TomorrowEra",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "FutureEra",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "ArcticFuture",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "OceanicFuture",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "VirtualFuture",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "SpaceAgeMars",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "SpaceAgeAsteroidBelt",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ],
#                 [
#                     {
#                         "__class__": "CampaignPvpRound"
#                     },
#                     {
#                         "era": "SpaceAgeVenus",
#                         "__class__": "CampaignPvpRanking"
#                     }
#                 ]
#             ],
#             "__class__": "EventHistoryOverview"
#         },
#         "requestClass": "OtherPlayerService",
#         "requestMethod": "getEventsPaginated",
#         "requestId": 35,
#         "__class__": "ServerResponse"
#     }
# ]

[
    {
        "__class__": "ServerRequest",
        "requestData": [
            9656396
        ],
        "requestClass": "FriendService",
        "requestMethod": "deleteFriend",
        "requestId": 27
    }
]

{
    "responseData": 9656396,
    "requestClass": "FriendService",
    "requestMethod": "deleteFriend",
    "requestId": 27,
    "__class__": "ServerResponse"
}
