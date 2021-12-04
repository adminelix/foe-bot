from collections import OrderedDict

import requests
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import has_inherited_table, declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class Model(Base):
    __abstract__ = True
    REQUEST_CLASS = None

    def __repr__(self):
        return "%s %s" % (self.__class__.__name__.title(), self.id)

    def __init__(self, *args, **kwargs):
        if '__class__' in kwargs:
            kwargs.pop('__class__')
        super(Model, self).__init__(*args, **kwargs)

    @declared_attr
    def __tablename__(cls):
        """
        """

        if has_inherited_table(cls):
            return None

        return cls.__name__.lower()

    @property
    def session(self):
        return inspect(self).session

    def populate(self, *args, **kwargs):
        for key, value in kwargs.items():

            if key in ['__class__']:
                continue

            setattr(self, key, value)

        return self

    def update(self, *args, **kwargs):
        return self.populate(*args, **kwargs)

    # TODO move that method to use cases
    @classmethod
    def request(cls, method, data, klass=None):
        klass = klass or cls.REQUEST_CLASS

        payload = [OrderedDict([
            ("requestId", "0"),
            ("__class__", "ServerRequest"),
            ("requestClass", klass),
            ("requestData", data),
            ("requestMethod", method),
            ("voClassName", "ServerRequest")]
        )]

        response = requests.get('', data=payload)

        return response
