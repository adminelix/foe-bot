from attr import define, field

from foe_bot.domain import structure
from foe_bot.domain.city_map_entity import CityMapEntity


def map_of_city_entities(list_: list[dict]) -> dict[int, CityMapEntity]:
    if type(list_) == list:
        return {v['id']: structure(v, CityMapEntity) for v in list_}


@define
class CityMap:
    gridId: str = field()
    unlocked_areas: list = field()
    tilesets: list = field()
    blocked_areas: list = field()
    klass: str = field(default=None)
    entities: dict[int, CityMapEntity] = field(converter=map_of_city_entities, default=dict[int, CityMapEntity])
    klass: str = field(default=None)

    def put_entities(self, entities: [CityMapEntity]) -> None:
        dict_ = {v.id: v for v in entities}
        if not self.entities:
            self.entities = dict_
        else:
            self.entities.update(dict_)
