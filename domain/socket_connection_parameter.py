import attr


@attr.s(init=False)
class SocketConnectionParameter:
    socketServerHost: str
    socketServerPort: int

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
