import attr

from foe_bot.domain.resources import ResourcesWrapper


@attr.define
class CurrentProduct:
    name: str = attr.attrib(default=None)
    production_time: int = attr.attrib(default=None)
    asset_name: str = attr.attrib(default=None)
    production_option: int = attr.attrib(default=None)
    product: ResourcesWrapper = attr.attrib(default=None)
    klass: str = attr.ib(default=None)


@attr.define
class State:
    current_product: CurrentProduct = attr.attrib(default=None)
    boosted: bool = attr.attrib(default=None)
    is_motivated: bool = attr.attrib(default=None)
    next_state_transition_in: int = attr.attrib(default=None)
    next_state_transition_at: int = attr.attrib(default=None)
    klass: str = attr.ib(default=None)


@attr.define
class CityMapEntity:
    id: int
    player_id: int
    cityentity_id: str
    type: str
    x: int
    y: int
    state: State
    connected: int = attr.ib(default=-1)
    unitSlots: list[dict] = attr.ib(default=[])
    klass: str = attr.ib(default=None)
