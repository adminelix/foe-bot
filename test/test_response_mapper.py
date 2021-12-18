import pickle

from domain.account import Account
from domain.city_map_entity import CityMapEntity
from foe_bot.response_mapper import map_to_account as map_
from foe_bot.util import foe_json_loads


def test_startup():
    acc = load_startup()
    assert len(acc.city_map.entities) == 72
    assert acc.resources.supplies == 426
    assert len(acc.hidden_rewards) == 8
    assert len(acc.players) == 4
    assert acc.city_user_data.player_id == 8365227


def test_start_production():
    acc = load_startup()

    ent: CityMapEntity = acc.city_map.entities[50]
    assert ent.state.klass == "ProductionFinishedState"

    u = open('start_production.json')
    data = foe_json_loads(u.read())

    map_(acc, *data)

    ent = acc.city_map.entities[50]
    assert ent.state.klass == "ProducingState"


def test_pickup_production():
    acc = load_startup()

    assert acc.city_map.entities[85].state.klass == "ProductionFinishedState"

    u = open('pickup_production.json')
    data = foe_json_loads(u.read())
    map_(acc, *data)

    assert acc.city_map.entities[85].state.klass == "ProducingState"
    assert acc.city_map.entities[85].state.next_state_transition_at == 1639507690


def load_startup():
    f = open('startup.json')
    data = foe_json_loads(f.read())
    acc = map_(Account(), *data)
    return acc
