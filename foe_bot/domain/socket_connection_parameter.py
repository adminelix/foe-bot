from attr import define, field


@define
class SocketConnectionParameter:
    socketServerHost: str = field()
    socketServerPort: int = field()
    klass: str = field()
