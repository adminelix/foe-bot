import attr


@attr.define
class HiddenReward:
    hiddenRewardId: int
    type: str
    startTime: int
    expireTime: int
    position: dict
    rarity: str
    animated: bool = attr.ib(default=False)
    klass: str = attr.ib(default=None)

    def __hash__(self):
        return hash(self.hiddenRewardId)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.hiddenRewardId == other.hiddenRewardId
