from attr import define, field


@define
class Clan:
    description: str = field()
    id: int = field()
    name: str = field()
    flag: str = field()
    klass: str = field(default=None)
