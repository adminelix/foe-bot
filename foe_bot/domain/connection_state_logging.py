import attr


@attr.define
class ConnectionStateLogging:
    intervalPools: dict[int, int]
    klass: str = attr.ib(default=None)

