import attr


@attr.s(init=False)
class CityMapEntity:
    id: int
    player_id: int
    cityentity_id: str
    type: str
    x: int
    y: int
    connected: int
    state: dict

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
