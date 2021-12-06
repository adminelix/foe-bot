import attr

from domain.city_map_entity import CityMapEntity


@attr.s(init=False)
class CityMap:
    gridId: str
    entities: list[CityMapEntity]

    # unlocked_areas = Column(String)
    # tilesets = Column(String)
    # blocked_areas = Column(Boolean)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
