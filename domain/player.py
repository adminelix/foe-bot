import attr

from domain.clan import Clan


@attr.s(init=False)
class Player:
    id: int
    incoming: bool
    accepted: bool
    registered: bool
    rewarded: bool
    score: int
    rank: int
    is_friend: bool
    is_neighbor: bool
    is_guild_member: bool
    isInvitedToClan: bool
    isInvitedFriend: bool
    is_self: bool
    profile_text: str
    city_name: str
    clan_id: int
    clan: Clan
    has_great_building: bool
    is_active: bool
    canSabotage: bool
    era: str
    showAvatarFrame: bool
    player_id: int
    name: str
    avatar: str
    is_online: bool
    next_interaction_in: int
    topAchievements: list

    def __init__(self, **kwargs):
        clan = kwargs.pop('clan', {})
        self.clan = Clan(**clan)
        self.__dict__.update(kwargs)
