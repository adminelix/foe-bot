import attr


@attr.s(init=False)
class Resources:
    expansions: int
    premium: int
    guild_expedition_attempt: int
    tavern_silver: int
    stars: int
    carnival_roses: int
    carnival_hearts: int
    spring_lanterns: int
    forge_bowl_footballs: int
    carnival_coins: int
    carnival_tickets: int
    soccer_energy: int
    summer_doubloons: int
    summer_compass: int
    fall_ingredient_apples: int
    fall_ingredient_pumpkins: int
    fall_ingredient_chocolate: int
    fall_ingredient_cinnamon: int
    fall_ingredient_caramel: int
    winter_matches: int
    archeology_brush: int
    archeology_shovel: int
    archeology_dynamite: int
    archeology_scroll: int
    halloween_candle: int
    halloween_flashlight: int
    halloween_lantern: int
    halloween_ticket: int
    winter_reindeer: int
    st_patricks_pot_of_gold: int
    soccer_tournament_tickets: int
    pvp_arena_attempt: int
    archeology_gem_shard: int
    wildlife_pop_moves: int
    wildlife_tickets: int
    wildlife_coins: int
    wildlife_booster_hammer: int
    wildlife_booster_color_changer: int
    wildlife_booster_color_destroyer: int
    halloween_joker_sticker: int
    winter_master_key_parts: int
    guild_perks_daily_donations: int
    strategy_points: int  # forge points
    money: int
    medals: int
    population: int
    total_population: int
    castle_points: int
    supplies: int

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
