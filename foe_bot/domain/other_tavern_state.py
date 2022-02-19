from attr import field, define


@define
class OtherTavernState:
    ownerId: int = field()
    state: str = field(default=None)
    unlockedChairCount: int = field(default=-1)
    sittingPlayerCount: int = field(default=-1)
    nextVisitTime: int = field(default=-1)
    klass: str = field(default=None)
