import cattr

from domain.city_map import CityMap
from domain.social_interaction_event import SocialInteractionEvent

cattr.register_structure_hook(CityMap, lambda d, t: CityMap.serialize(**d))
cattr.register_structure_hook(SocialInteractionEvent, lambda d, t: SocialInteractionEvent.serialize(**d))
