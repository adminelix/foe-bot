import attr


@attr.define
class StaticData:
    identifier: str
    url: str
    klass: str = attr.ib(default=None)

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.identifier == other.identifier
