import attr


@attr.s(init=False)
class Time:
    time: int

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
