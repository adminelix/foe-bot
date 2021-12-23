import attr
from cattr import structure

from foe_bot.domain.player import Player
from foe_bot.util import parse_date


@attr.define
class CityGood:
    good_id: str = attr.ib(default=None)
    value: int = attr.ib(default=None)
    klass: str = attr.ib(default=None)


@attr.define
class SocialInteractionEvent:
    expansions: int = attr.ib(default=None)
    interaction_type: str = attr.ib(default=None)
    entity_id: str = attr.ib(default=None)
    id: int = attr.ib(default=None)
    player_id: int = attr.ib(default=None)
    date: int = attr.ib(default=None)
    other_player: Player = attr.ib(default=None)
    type: str = attr.ib(default=None)
    level: int = attr.ib(default=None)
    achievementName: str = attr.ib(default=None)
    offer: CityGood = attr.ib(default=None)
    need: CityGood = attr.ib(default=None)
    city_map_entity_id: str = attr.ib(default=None)
    cityentity_id: int = attr.ib(default=None)
    klass: str = attr.ib(default=None)

    @staticmethod
    def serialize(**kwargs):
        return SocialInteractionEvent(
            date=parse_date(kwargs.pop('date')) if 'date' in kwargs.keys() else None,
            other_player=structure(kwargs.pop('other_player'), Player) if 'other_player' in kwargs.keys() else None,
            **kwargs)
