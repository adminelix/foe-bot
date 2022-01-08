import attr

from foe_bot.domain.resources import ResourcesWrapper


@attr.define
class ChairUnlockCost:
    premiumCosts: ResourcesWrapper
    normalCosts: ResourcesWrapper
    klass: str = attr.ib(default=None)


@attr.define
class TableUnlockCost:
    premiumCosts: ResourcesWrapper
    normalCosts: ResourcesWrapper
    klass: str = attr.ib(default=None)


@attr.define
class UnlockCost:
    premiumCosts: ResourcesWrapper
    normalCosts: ResourcesWrapper
    klass: str = attr.ib(default=None)


@attr.define
class Customization:
    id: str
    type: str
    name: str
    description: str
    unlockCosts: UnlockCost = attr.ib(default=None)
    requiredCustomizationIds: list[str] = attr.ib(default=list[str])
    klass: str = attr.ib(default=None)


@attr.define
class TavernConfig:
    chairUnlockCosts: list[ChairUnlockCost]
    tableUnlockCosts: list[TableUnlockCost]
    customizations: list[Customization]
    klass: str = attr.ib(default=None)
