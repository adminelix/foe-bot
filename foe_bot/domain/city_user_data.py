import attr


@attr.define
class CityUserData:
    player_id: int
    city_name: str
    user_name: str
    era: str
    profile_text: str
    portrait_id: str
    unlocked_avatars: str
    clan_name: str
    time_left_to_validate_email: bool
    hasPiiAccess: bool
    canSetEmail: bool
    createdAt: int
    isRealEmail: bool = attr.attrib(default=False)
    is_guest: bool = attr.attrib(default=False)
    has_new_neighbors: bool = attr.attrib(default=False)
    has_new_event: bool = attr.attrib(default=False)
    email_validated: bool = attr.attrib(default=False)
    is_tester: bool = attr.attrib(default=False)
    rank: int = attr.attrib(default=None)
    klass: str = attr.ib(default=None)
