import attr


@attr.define
class ConnectionStateLogging:
    intervalPools: dict[str, int]
    klass: str = attr.ib(default=None)

