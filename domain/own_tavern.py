import attr


@attr.define
class SelectedCustomizationIds:
    tablecloth: str
    tray: str
    flooring: str


@attr.define
class Visitor:
    player_id: int
    name: str
    avatar: str
    klass: str


@attr.define
class View:
    tableLevel: int
    unlockedChairs: int
    visitors: list[Visitor]
    selectedCustomizationIds: SelectedCustomizationIds
    tavernSilverBase: int
    tavernSilverAdd: int
    klass: str


@attr.define
class OwnTavern:
    view: View
    unlockedCustomizationIds: list[str]
    friendCount: int
