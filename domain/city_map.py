import attr

from domain.city_map_entity import CityMapEntity


@attr.s(init=False)
class CityMap:
    gridId: str
    entities: dict[int, CityMapEntity] = {}

    unlocked_areas: list = []
    tilesets: list = []
    blocked_areas: list = []

    def __init__(self, **kwargs):
        entities = kwargs.pop('entities', {})
        self.put_entities(*entities)
        self.__dict__.update(kwargs)

    def put_entities(self, *args) -> None:
        for arg in args:
            entity = CityMapEntity(**arg)
            self.entities[entity.id] = entity
