import attr


@attr.s(init=False)
class HiddenReward:
    hiddenRewardId: int
    type: str
    startTime: int
    expireTime: int
    position: dict
    animated: bool
    rarity: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
