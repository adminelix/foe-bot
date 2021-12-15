import attr


@attr.s(init=False)
class Clan:
    description: str
    id: int
    name: str
    flag: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
