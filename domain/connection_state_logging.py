import attr


@attr.s(init=False)
class ConnectionStateLogging:
    intervalPools: dict[str, int] = {}

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
