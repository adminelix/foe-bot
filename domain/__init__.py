import cattr

from domain.city_map import CityMap

cattr.register_structure_hook(CityMap, lambda d, t: CityMap.serialize(**d))
