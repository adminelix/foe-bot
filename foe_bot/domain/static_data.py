from attr import field, define


@define
class StaticData:
    identifier: str = field()
    url: str = field()
    klass: str = field()

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.identifier == other.identifier
