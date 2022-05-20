from attr import define, field

from foe_bot.domain.resources import Resources


@define
class ResourcePackage:
    klass: str = field()
    cost: Resources = field()
    gain: int = field()

@define
class Item:
    klass: str = field()
    upgradeItemId: str = field(default=None)
    selectionKitId: str = field(default=None)
    target: str = field(default=None)
    duration: str = field(default=None)
    resource_package: ResourcePackage = field(default=None)


@define
class Value:
    trade_coins: int = field()
    gemstones: float = field()


@define
class ExchangeBaseValue:
    minValues: Value = field()
    maxValues: Value = field()
    klass: str = field()


@define
class InventoryItem:
    id: int = field()
    name: str = field()
    description: str = field()
    inStock: int = field()
    item: Item = field()
    itemAssetName: str = field()
    sortPriority: list[int] = field()
    klass: str = field()
    exchangeBaseValue: ExchangeBaseValue = field(default=None)
