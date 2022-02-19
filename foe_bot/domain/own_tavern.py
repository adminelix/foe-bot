from attr import define, field


@define
class SelectedCustomizationIds:
    tablecloth: str = field()
    tray: str = field()
    flooring: str = field()


@define
class Visitor:
    player_id: int = field()
    name: str = field()
    avatar: str = field()
    klass: str = field()


@define
class View:
    tableLevel: int = field()
    unlockedChairs: int = field()
    visitors: list[Visitor] = field()
    selectedCustomizationIds: SelectedCustomizationIds = field()
    tavernSilverBase: int = field()
    tavernSilverAdd: int = field()
    klass: str = field()


@define
class OwnTavern:
    view: View = field()
    unlockedCustomizationIds: list[str] = field()
    friendCount: int = field()
