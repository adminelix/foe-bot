from attr import define, attrib

from foe_bot.domain.clan import Clan


@define
class Player:
    player_id: int = attrib(default=-1)
    id: int = attrib(default=None)
    incoming: bool = attrib(default=None)
    accepted: bool = attrib(default=None)
    registered: bool = attrib(default=None)
    rewarded: bool = attrib(default=None)
    score: int = attrib(default=None)
    rank: int = attrib(default=None)
    is_friend: bool = attrib(default=None)
    is_neighbor: bool = attrib(default=None)
    is_guild_member: bool = attrib(default=None)
    isInvitedToClan: bool = attrib(default=None)
    isInvitedFriend: bool = attrib(default=None)
    is_self: bool = attrib(default=None)
    profile_text: str = attrib(default=None)
    city_name: str = attrib(default=None)
    clan_id: int = attrib(default=None)
    clan: Clan = attrib(default=None)
    has_great_building: bool = attrib(default=None)
    is_active: bool = attrib(default=None)
    canSabotage: bool = attrib(default=None)
    era: str = attrib(default=None)
    showAvatarFrame: bool = attrib(default=None)
    name: str = attrib(default=None)
    avatar: str = attrib(default=None)
    is_online: bool = attrib(default=None)
    topAchievements: list = attrib(default=None)
    title: str = attrib(default=None)
    won_battles: int = attrib(default=None)
    next_interaction_in: int = attrib(default=None)
    klass: str = attrib(default=None)

    def __hash__(self):
        return hash(self.player_id)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.player_id == other.player_id
