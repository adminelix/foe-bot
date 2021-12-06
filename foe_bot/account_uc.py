from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref

from domain.city_map import CityMap
from domain.city_user_data import CityUserData
from domain.db import Base


class Account(Base):
    def update_from_response(self, *args) -> Account:
        for arg in args:
            if type(arg['responseData']) == list:
                for data in arg['responseData']:
                    if type(data) == dict:
                        self.__populate_item(**data)
            elif type(arg['responseData']) == dict:
                if arg['responseData']['__class__']:
                    self.__populate_item(**arg['responseData'])
                else:
                    for item in arg['responseData']:
                        self.__populate_item(**item)
            else:
                print('cannot handle: ' + repr(arg))
        return self

    def __populate_item(self, **kwargs) -> None:
        subclasses = Base.__subclasses__()
        gen = (subclass for subclass in subclasses if subclass.__tablename__ == kwargs['__class__'])
        subclass = next(gen, None)

        if 'Startup' == kwargs['__class__']:
            self.city_user_data.update(**kwargs['user_data'])
            # self.city_map.update(**kwargs['city_map'])

        if subclass is None:
            print("no implementation for class: " + repr(kwargs))
            return

        obj = subclass()
        if isinstance(obj, CityUserData):
            self.city_user_data.update(**kwargs)
