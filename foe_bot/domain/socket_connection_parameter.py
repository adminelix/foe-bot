from attr import field, define


@define
class SocketConnectionParameter:
    socketServerHost: str = field()
    socketServerPort: int = field()
    klass: str = field()
