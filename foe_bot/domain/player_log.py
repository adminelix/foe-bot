from attr import field, define


@define
class PlayerLog:
    player_id: int = field()
    invited_at: int = field(default=-1)
    invite_blocked_until: int = field(default=-1)
