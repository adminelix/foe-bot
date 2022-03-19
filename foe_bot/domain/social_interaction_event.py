from attr import define, field

from foe_bot.domain.player import Player
from foe_bot.util import parse_date


@define
class CityGood:
    good_id: str = field()
    value: int = field()
    klass: str = field()


@define
class SocialInteractionEvent:
    klass: str = field()

    date: int = field(converter=parse_date, default="-1")
    type: str = field(default=None)
    id: int = field(default=None)
    other_player: Player = field(default=None)
    interaction_type: str = field(default=None)
    status: str = field(default=None)
    expansions: int = field(default=None)
    entity_id: str = field(default=None)
    level: int = field(default=None)
    achievementName: str = field(default=None)
    offer: CityGood = field(default=None)
    need: CityGood = field(default=None)
    city_map_entity_id: str = field(default=None)
    cityentity_id: str = field(default=None)
    new_era: str = field(default=None)
    battle_id: int = field(default=None)
    great_building_name: str = field(default=None)
    rank: int = field(default=None)
    messageContent: str = field(default=None)
