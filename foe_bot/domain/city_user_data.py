import attr


@attr.define
class CityUserData:
    player_id: int
    city_name: str
    user_name: str
    era: str
    is_tester: bool
    profile_text: str
    portrait_id: str
    unlocked_avatars: str
    clan_name: str
    email_validated: bool
    time_left_to_validate_email: bool
    has_new_event: bool
    has_new_neighbors: bool
    is_guest: bool
    hasPiiAccess: bool
    canSetEmail: bool
    isRealEmail: bool
    createdAt: int
    rank: int = attr.attrib(default=None)
    klass: str = attr.ib(default=None)
