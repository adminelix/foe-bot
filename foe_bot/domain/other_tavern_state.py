import attr


@attr.define
class OtherTavernState:
    ownerId: int
    state: str = attr.ib(default=None)
    unlockedChairCount: int = attr.ib(default=-1)
    sittingPlayerCount: int = attr.ib(default=-1)
    nextVisitTime: int = attr.ib(default=-1)
    klass: str = attr.ib(default=None)
