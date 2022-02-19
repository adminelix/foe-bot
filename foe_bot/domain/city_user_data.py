from attr import define, field


@define
class CityUserData:
    player_id: int = field()
    city_name: str = field()
    user_name: str = field()
    era: str = field()
    profile_text: str = field()
    portrait_id: str = field()
    unlocked_avatars: str = field()
    clan_name: str = field()
    time_left_to_validate_email: bool = field()
    hasPiiAccess: bool = field()
    canSetEmail: bool = field()
    createdAt: int = field()
    isRealEmail: bool = field(default=False)
    is_guest: bool = field(default=False)
    has_new_neighbors: bool = field(default=False)
    has_new_event: bool = field(default=False)
    email_validated: bool = field(default=False)
    is_tester: bool = field(default=False)
    rank: int = field(default=None)
    klass: str = field(default=None)
