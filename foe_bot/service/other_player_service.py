import json
import logging
import sys
import time

from foe_bot import cfg
from foe_bot.domain.player import Player
from foe_bot.domain.player_log import PlayerLog
from foe_bot.service.abstract_service import AbstractService


class OtherPlayerService(AbstractService):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__last_events_refresh = sys.maxsize
        self.__last_players_refresh = 0
        self.__refresh_players_interval = 15 * 60  # in seconds
        self.__config = cfg.get('other_player_service')

    def do(self):
        self._refresh_player()
        self._update_events()
        if self.__config.get('moppel', None):
            self._moppel()
        if self.__config.get('manage_friends', None):
            self._accept_friend_invites()
            self._revoke_friend_invites()
            self._remove_useless_friends()
            self._send_friend_invites()

    def _moppel(self):
        player_map = self._acc.players
        count = 0
        player_to_moppel = [player for (key, player) in player_map.items()
                            if not player.next_interaction_in and not player.isInvitedFriend]

        for player in player_to_moppel:
            success = self._client.send('OtherPlayerService', 'polivateRandomBuilding', [player.player_id])

            if success:
                count += 1

        if count > 0:
            self.__logger.info(f"moppeled {len(player_to_moppel)} player")

    def _accept_friend_invites(self):
        player_map = self._acc.players
        max_friends = 140
        friends_amount = len([player for (key, player) in player_map.items() if player.is_friend])

        if friends_amount < max_friends:
            player_to_accept = [player for (key, player) in player_map.items()
                                if player.isInvitedFriend and player.incoming and not player.accepted]

            for player in player_to_accept:
                success = self._client.send('FriendService', 'acceptInvitation', [player.player_id])

                if success:
                    self.__logger.info(f"accept friend invite from {player.name}")

            self._refresh_player()

    def _send_friend_invites(self):
        now = int(time.time())
        player_map = self._acc.players
        player_logs = self._acc.player_logs
        max_friends = 80
        max_invitations = 130
        friends_amount = len([player for (key, player) in player_map.items() if player.is_friend])
        invitations_amount = len([player for (key, player) in player_map.items() if player.isInvitedFriend])
        free_slots = max_friends - friends_amount

        if friends_amount + invitations_amount < max_invitations:
            player_to_invite = self.__filter_players_to_invite(now, player_logs, player_map)

            for player in player_to_invite:
                successful = self._client.send('FriendService', 'invitePlayerById', [player.player_id])
                log = player_logs.get(player.player_id, PlayerLog(player.player_id))
                if successful:
                    log.invited_at = int(time.time())
                    self.__logger.info(f"send friend invite to '{player.name}'")
                    free_slots -= 1

                log.invite_blocked_until = int(time.time()) * (60 * 60 * 24 * 30)
                self._acc.put_player_log([log])
                if free_slots < 1:
                    break

    def _revoke_friend_invites(self):
        now = int(time.time())
        player_to_revoke = self.__filter_player_with_expired_friends_invite(now)

        for player in player_to_revoke:
            successful = self._client.send('FriendService', 'deleteFriend', [player.player_id])

            if successful:
                self._acc.players.get(player.player_id).isInvitedFriend = False

                player_log = self._acc.player_logs.get(player.player_id, PlayerLog(player.player_id))
                player_log.invited_at = -1
                player_log.invite_blocked_until = now + (60 * 60 * 24 * 30)
                self._acc.put_player_log([player_log])

                self.__logger.info(f"revoke friends invite to '{player.name}'")

    def _remove_useless_friends(self):
        now = int(time.time())

        useless_friends = self.__filter_useless_friends(now)

        for player in useless_friends:
            successful = self._client.send('FriendService', 'deleteFriend', [player.player_id])

            if successful:
                self._acc.players.get(player.player_id).is_friend = False

                player_log = self._acc.player_logs.get(player.player_id, PlayerLog(player.player_id))
                player_log.invited_at = -1
                player_log.invite_blocked_until = now + (60 * 60 * 24 * 30)
                self._acc.put_player_log([player_log])

                self.__logger.info(f"removed useless friend '{player.name}'")

    def _refresh_player(self):
        now = int(time.time())
        if self.__last_players_refresh + self.__refresh_players_interval < now or len(self._acc.players) == 0:
            self._acc.players = dict[int, Player]()
            self.__refresh_neighbor_list()  # must be refreshed at first because does not include all data about player
            self.__refresh_friend_list()  # overwrites object if friend is neighbor with more attributes
            self.__refresh_clan_member_list()
            self.__last_players_refresh = now

            self.__logger.info(f"refreshed players")

    def _update_events(self):
        now = int(time.time())
        last_event_time: int = 0
        events = self._acc.events
        for event in events.values():
            last_event_time = event.date if event.date > last_event_time else last_event_time

        one_hour_ago = now - (60 * 60)
        six_hours_ago = now - (60 * 60 * 6)
        if last_event_time < six_hours_ago and self.__last_events_refresh > one_hour_ago:
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

            success = self._client.send('OtherPlayerService', 'getEventsPaginated', [raw_body])

            if success:
                self.__cleanup_events()
                self.__last_events_refresh = now
                self.__logger.info(f"updated events")

    def __cleanup_events(self):
        four_weeks_ago = int(time.time()) - (60 * 60 * 24 * 28)
        keys = self._acc.events.keys()
        for key in keys:
            if self._acc.events.get(key).date < four_weeks_ago:
                self._acc.events.pop(key)

    def __filter_players_to_invite(self, now, player_logs, player_map):
        player_to_invite = [player for (key, player) in player_map.items()
                            if not player.isInvitedFriend
                            and not player.is_friend
                            and player.is_active
                            and player_logs.get(player.player_id,
                                                PlayerLog(player.player_id)).invite_blocked_until < now]
        return player_to_invite

    def __filter_player_with_expired_friends_invite(self, now: int) -> list[Player]:
        before_7_days = now - (60 * 60 * 24 * 7)
        player_map = self._acc.players
        player_logs = self._acc.player_logs
        player_to_revoke = [player for player in player_map.values()
                            if player.isInvitedFriend
                            and not player.is_friend
                            and player_logs.get(player.player_id,
                                                PlayerLog(player.player_id)).invited_at < before_7_days]
        return player_to_revoke

    def __filter_useless_friends(self, now: int) -> list[Player]:
        before_7_days = now - (60 * 60 * 24 * 7)
        player_map = self._acc.players
        events = self._acc.events
        friends = {key: player for (key, player) in player_map.items() if player.is_friend}
        moppeling_player_ids = set([event.other_player.player_id for event in events.values()
                                    if event.date > before_7_days
                                    and (event.interaction_type in ['motivate', 'polish']
                                         or 'friend_tavern_sat_down' in event.type)])
        fresh_friendships_ids = set([event.other_player.player_id for event in events.values() if
                                     event.type == 'friend_accepted' and event.date > before_7_days])
        useless_friends = [player for player in friends.values() if
                           player.player_id not in moppeling_player_ids and player.player_id not in fresh_friendships_ids]
        return useless_friends

    def __refresh_neighbor_list(self):
        self._client.send('OtherPlayerService', 'getNeighborList', [])

    def __refresh_friend_list(self):
        self._client.send('OtherPlayerService', 'getFriendsList', [])

    def __refresh_clan_member_list(self):
        if len(self._acc.city_user_data.clan_name) > 0:
            self._client.send('OtherPlayerService', 'getClanMemberList', [])
