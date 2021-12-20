import attr


@attr.define
class PlayerLog:
    player_id: int
    invited_at: int = attr.attrib(default=-1)
    invite_blocked_until: int = attr.attrib(default=-1)
