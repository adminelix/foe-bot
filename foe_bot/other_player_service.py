import logging
import time

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class OtherPlayerService:

    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__last_refresh = 0
        self.__refresh_interval = 15 * 60  # in seconds

    def moppel(self):
        self.__refresh_player()
        player_map = self.__acc.players
        player_to_moppel = [player for (key, player) in player_map.items()
                            if player.next_interaction_in == 0 and not player.isInvitedFriend]

        for player in player_to_moppel:
            body = self.__request_session.create_rest_body('OtherPlayerService', 'polivateRandomBuilding',
                                                           [player.player_id])
            response = self.__request_session.send(body)
            map_to_account(self.__acc, *response)

        if len(player_to_moppel) > 0:
            self.__logger.info(f"moppeled {len(player_to_moppel)} player")

    def accept_friend_invites(self):
        max_friends = 140
        player_map = self.__acc.players
        # TODO if amount of friends < 80

        friends_amount = len([player for (key, player) in player_map.items() if player.is_friend])

        if friends_amount < max_friends:
            player_to_accept = [player for (key, player) in player_map.items()
                                if player.isInvitedFriend and player.incoming and not player.accepted]

            for player in player_to_accept:
                body = self.__request_session.create_rest_body('FriendService', 'acceptInvitation', [player.player_id])
                response = self.__request_session.send(body)
                map_to_account(self.__acc, *response)
                self.__logger.info(f"accept friend invite from {player.name}")

    def __refresh_player(self):
        now = int(time.time())
        if self.__last_refresh + self.__refresh_interval < now:
            self.__refresh_friend_list()
            self.__refresh_clan_member_list()
            self.__refresh_neighbor_list()
            self.__last_refresh = now

            self.__logger.info(f"players refreshed")

    def __refresh_neighbor_list(self):
        body = self.__request_session.create_rest_body('OtherPlayerService', 'getNeighborList', [])
        response = self.__request_session.send(body)
        map_to_account(self.__acc, *response)

    def __refresh_friend_list(self):
        body = self.__request_session.create_rest_body('OtherPlayerService', 'getFriendsList', [])
        response = self.__request_session.send(body)
        map_to_account(self.__acc, *response)

    def __refresh_clan_member_list(self):
        if len(self.__acc.city_user_data.clan_name) > 0:
            body = self.__request_session.create_rest_body('OtherPlayerService', 'getClanMemberList', [])
            response = self.__request_session.send(body)
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
