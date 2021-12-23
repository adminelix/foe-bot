import attr


@attr.define
class SocketConnectionParameter:
    socketServerHost: str
    socketServerPort: int
    klass: str = attr.ib(default=None)
