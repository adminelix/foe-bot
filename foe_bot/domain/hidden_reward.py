from attr import define, field


@define
class HiddenReward:
    hiddenRewardId: int = field()
    type: str = field()
    startTime: int = field()
    expireTime: int = field()
    position: dict = field()
    rarity: str = field()
    animated: bool = field(default=False)
    klass: str = field(default=None)

    def __hash__(self):
        return hash(self.hiddenRewardId)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.hiddenRewardId == other.hiddenRewardId
