import cattr

from foe_bot.domain.city_map import CityMap
from foe_bot.domain.social_interaction_event import SocialInteractionEvent
from foe_bot.domain.time import Time

cattr.register_structure_hook(Time, lambda d, t: Time.serialize(**d))
cattr.register_structure_hook(CityMap, lambda d, t: CityMap.serialize(**d))
