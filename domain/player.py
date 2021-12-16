import attr

from domain.clan import Clan


@attr.define
class Player:
    player_id: int
    id: int = attr.attrib(default=None)
    incoming: bool = attr.attrib(default=None)
    accepted: bool = attr.attrib(default=None)
    registered: bool = attr.attrib(default=None)
    rewarded: bool = attr.attrib(default=None)
    score: int = attr.attrib(default=None)
    rank: int = attr.attrib(default=None)
    is_friend: bool = attr.attrib(default=None)
    is_neighbor: bool = attr.attrib(default=None)
    is_guild_member: bool = attr.attrib(default=None)
    isInvitedToClan: bool = attr.attrib(default=None)
    isInvitedFriend: bool = attr.attrib(default=None)
    is_self: bool = attr.attrib(default=None)
    profile_text: str = attr.attrib(default=None)
    city_name: str = attr.attrib(default=None)
    clan_id: int = attr.attrib(default=None)
    clan: Clan = attr.attrib(default=None)
    has_great_building: bool = attr.attrib(default=None)
    is_active: bool = attr.attrib(default=None)
    canSabotage: bool = attr.attrib(default=None)
    era: str = attr.attrib(default=None)
    showAvatarFrame: bool = attr.attrib(default=None)
    name: str = attr.attrib(default=None)
    avatar: str = attr.attrib(default=None)
    is_online: bool = attr.attrib(default=None)
    topAchievements: list = attr.attrib(default=None)
    title: str = attr.attrib(default=None)
    won_battles: int = attr.attrib(default=None)
    next_interaction_in: int = attr.attrib(default=None)
    klass: str = attr.ib(default=None)

    def __hash__(self):
        return hash(self.player_id)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.player_id == other.player_id
