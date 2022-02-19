from attr import define, field

from foe_bot.domain.clan import Clan


@define
class Player:
    player_id: int = field(default=-1)
    id: int = field(default=None)
    incoming: bool = field(default=None)
    accepted: bool = field(default=None)
    registered: bool = field(default=None)
    rewarded: bool = field(default=None)
    score: int = field(default=None)
    rank: int = field(default=None)
    is_friend: bool = field(default=None)
    is_neighbor: bool = field(default=None)
    is_guild_member: bool = field(default=None)
    isInvitedToClan: bool = field(default=None)
    isInvitedFriend: bool = field(default=None)
    is_self: bool = field(default=None)
    profile_text: str = field(default=None)
    city_name: str = field(default=None)
    clan_id: int = field(default=None)
    clan: Clan = field(default=None)
    has_great_building: bool = field(default=None)
    is_active: bool = field(default=None)
    canSabotage: bool = field(default=None)
    era: str = field(default=None)
    showAvatarFrame: bool = field(default=None)
    name: str = field(default=None)
    avatar: str = field(default=None)
    is_online: bool = field(default=None)
    topAchievements: list = field(default=None)
    title: str = field(default=None)
    won_battles: int = field(default=None)
    next_interaction_in: int = field(default=None)
    klass: str = field(default=None)

    def __hash__(self):
        return hash(self.player_id)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.player_id == other.player_id
