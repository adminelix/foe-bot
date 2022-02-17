from attr import attrib, define

from foe_bot.domain.player import Player
from foe_bot.util import parse_date


@define
class CityGood:
    good_id: str = attrib()
    value: int = attrib()
    klass: str = attrib()


@define
class SocialInteractionEvent:
    id: int = attrib()
    player_id: int = attrib()
    date = attrib(converter=parse_date)
    klass: str = attrib()
    type: str = attrib()

    other_player: Player = attrib(default=None)
    interaction_type: str = attrib(default=None)
    status: str = attrib(default=None)
    expansions: int = attrib(default=None)
    entity_id: str = attrib(default=None)
    level: int = attrib(default=None)
    achievementName: str = attrib(default=None)
    offer: CityGood = attrib(default=None)
    need: CityGood = attrib(default=None)
    city_map_entity_id: str = attrib(default=None)
    cityentity_id: str = attrib(default=None)
    new_era: int = attrib(default=None)
    battle_id: int = attrib(default=None)
    great_building_name = attrib(default=None)
    rank = attrib(default=None)
    messageContent: int = attrib(default=None)
