from attr import define, field


@define
class ConnectionStateLogging:
    intervalPools: dict[int, int] = field()
    klass: str = field(default=None)
