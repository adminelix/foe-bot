from __future__ import annotations

import attr

from domain.city_map import CityMap
from domain.city_user_data import CityUserData


@attr.s(init=False)
class Account:
    user_name: str
    city_user_data: CityUserData
    city_map: CityMap

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
