import attr


@attr.define
class Resources:
    expansions: int = attr.ib(default=None)
    premium: int = attr.ib(default=None)
    guild_expedition_attempt: int = attr.ib(default=None)
    tavern_silver: int = attr.ib(default=None)
    stars: int = attr.ib(default=None)
    carnival_roses: int = attr.ib(default=None)
    carnival_hearts: int = attr.ib(default=None)
    spring_lanterns: int = attr.ib(default=None)
    forge_bowl_footballs: int = attr.ib(default=None)
    carnival_coins: int = attr.ib(default=None)
    carnival_tickets: int = attr.ib(default=None)
    soccer_energy: int = attr.ib(default=None)
    summer_doubloons: int = attr.ib(default=None)
    summer_compass: int = attr.ib(default=None)
    fall_ingredient_apples: int = attr.ib(default=None)
    fall_ingredient_pumpkins: int = attr.ib(default=None)
    fall_ingredient_chocolate: int = attr.ib(default=None)
    fall_ingredient_cinnamon: int = attr.ib(default=None)
    fall_ingredient_caramel: int = attr.ib(default=None)
    winter_matches: int = attr.ib(default=None)
    archeology_brush: int = attr.ib(default=None)
    archeology_shovel: int = attr.ib(default=None)
    archeology_dynamite: int = attr.ib(default=None)
    archeology_scroll: int = attr.ib(default=None)
    halloween_candle: int = attr.ib(default=None)
    halloween_flashlight: int = attr.ib(default=None)
    halloween_lantern: int = attr.ib(default=None)
    halloween_ticket: int = attr.ib(default=None)
    winter_reindeer: int = attr.ib(default=None)
    st_patricks_pot_of_gold: int = attr.ib(default=None)
    soccer_tournament_tickets: int = attr.ib(default=None)
    pvp_arena_attempt: int = attr.ib(default=None)
    archeology_gem_shard: int = attr.ib(default=None)
    wildlife_pop_moves: int = attr.ib(default=None)
    wildlife_tickets: int = attr.ib(default=None)
    wildlife_coins: int = attr.ib(default=None)
    wildlife_booster_hammer: int = attr.ib(default=None)
    wildlife_booster_color_changer: int = attr.ib(default=None)
    wildlife_booster_color_destroyer: int = attr.ib(default=None)
    halloween_joker_sticker: int = attr.ib(default=None)
    winter_master_key_parts: int = attr.ib(default=None)
    guild_perks_daily_donations: int = attr.ib(default=None)
    strategy_points: int = attr.ib(default=None)  # forge points
    money: int = attr.ib(default=None)
    medals: int = attr.ib(default=None)
    population: int = attr.ib(default=None)
    total_population: int = attr.ib(default=None)
    castle_points: int = attr.ib(default=None)
    supplies: int = attr.ib(default=None)


@attr.define
class ResourcesWrapper:
    resources: Resources
    klass: str
