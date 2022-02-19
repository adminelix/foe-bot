import sys

from attr import define, field

from foe_bot.domain.resources import ResourcesWrapper


@define
class CurrentProduct:
    name: str = field(default=None)
    production_time: int = field(default=None)
    asset_name: str = field(default=None)
    production_option: int = field(default=None)
    product: ResourcesWrapper = field(default=None)
    klass: str = field(default=None)


@define
class State:
    current_product: CurrentProduct = field(default=None)
    boosted: bool = field(default=None)
    is_motivated: bool = field(default=None)
    next_state_transition_in: int = field(default=-1)
    next_state_transition_at: int = field(default=sys.maxsize)
    klass: str = field(default=None)


@define
class CityMapEntity:
    id: int = field()
    player_id: int = field()
    cityentity_id: str = field()
    type: str = field()
    x: int = field()
    y: int = field()
    state: State = field()
    connected: int = field(default=-1)
    unitSlots: list[dict] = field(default=[])
    klass: str = field(default=None)
