import attr


@attr.define
class Clan:
    description: str
    id: int
    name: str
    flag: str
    klass: str = attr.ib(default=None)
