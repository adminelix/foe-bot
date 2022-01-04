import json
import logging
import time

from foe_bot import cfg
from foe_bot.domain.account import Account
from foe_bot.domain.player import Player
from foe_bot.domain.player_log import PlayerLog
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
        count = 0
        player_to_moppel = [player for (key, player) in player_map.items()
                            if not player.next_interaction_in and not player.isInvitedFriend]

        for player in player_to_moppel:
            body = self.__request_session.create_rest_body('OtherPlayerService', 'polivateRandomBuilding',
                                                           [player.player_id])
            response, success = self.__request_session.send(body)
            map_to_account(self.__acc, *response)
            if success:
                count += 1

        if count > 0:
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
        max_friends = 80
        max_invitations = 130
        friends_amount = len([player for (key, player) in player_map.items() if player.is_friend])
        invitations_amount = len([player for (key, player) in player_map.items() if player.isInvitedFriend])
        free_slots = max_friends - friends_amount

        if friends_amount + invitations_amount < max_invitations:
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
        if self.__last_refresh + self.__refresh_interval < now or len(self.__acc.players) == 0:
            self.__acc.players = dict[int, Player]()
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
