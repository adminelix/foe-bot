import attr
from cattr import structure

from foe_bot.domain.city_map_entity import CityMapEntity


def map_of_city_entities(list_: list[CityMapEntity]) -> dict[int, CityMapEntity]:
    if type(list_) == list:
        return {v.id: v for v in list_}


@attr.define
class CityMap:
    gridId: str
    unlocked_areas: list
    tilesets: list
    blocked_areas: list
    klass: str = attr.attrib(default=None)
    entities: dict[int, CityMapEntity] = attr.attrib(default=dict[int, CityMapEntity])
    klass: str = attr.ib(default=None)

    @staticmethod
    def serialize(**kwargs):
        return CityMap(entities=structure({v['id']: v for v in kwargs.pop('entities')}, dict[int, CityMapEntity]),
                       **kwargs)

    def put_entities(self, entities: [CityMapEntity]) -> None:
        dict_ = map_of_city_entities(entities)
        if not self.entities:
            self.entities = dict_
        else:
            self.entities.update(dict_)
