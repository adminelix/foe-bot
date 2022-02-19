from attr import define, field

from foe_bot.domain.resources import ResourcesWrapper


@define
class ChairUnlockCost:
    premiumCosts: ResourcesWrapper = field()
    normalCosts: ResourcesWrapper = field()
    klass: str = field(default=None)


@define
class TableUnlockCost:
    premiumCosts: ResourcesWrapper = field()
    normalCosts: ResourcesWrapper = field()
    klass: str = field(default=None)


@define
class UnlockCost:
    premiumCosts: ResourcesWrapper = field()
    normalCosts: ResourcesWrapper = field()
    klass: str = field(default=None)


@define
class Customization:
    id: str = field()
    type: str = field()
    name: str = field()
    description: str = field()
    unlockCosts: UnlockCost = field(default=None)
    requiredCustomizationIds: list[str] = field(default=list[str])
    klass: str = field(default=None)


@define
class TavernConfig:
    chairUnlockCosts: list[ChairUnlockCost]
    tableUnlockCosts: list[TableUnlockCost]
    customizations: list[Customization]
    klass: str = field(default=None)
