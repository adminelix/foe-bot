import attr


@attr.define
class HiddenReward:
    hiddenRewardId: int
    type: str
    startTime: int
    expireTime: int
    position: dict
    animated: bool
    rarity: str
    klass: str = attr.ib(default=None)

    def __hash__(self):
        return hash(self.hiddenRewardId)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.hiddenRewardId == other.hiddenRewardId
