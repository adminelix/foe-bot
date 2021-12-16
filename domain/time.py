import attr


@attr.define
class Time:
    time: int
    klass: str = attr.ib(default=None)
