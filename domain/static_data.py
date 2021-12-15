import attr


@attr.s(init=False)
class StaticData:
    identifier: str
    url: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
