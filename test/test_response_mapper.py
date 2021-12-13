import json

from domain.account import Account
from foe_bot.response_mapper import map_to_account as map_


def test_startup():
    acc = load_startup()
    assert len(acc.city_map.entities) == 41


def test_start_production():
    acc = load_startup()
    assert acc.city_map.entities[31].state['__class__'] == "ProductionFinishedState"

    u = open('start_production.json')
    data = json.load(u)

    map_(Account(), *data)

    assert acc.city_map.entities[31].state['__class__'] == "ProducingState"


def test_pickup_production():
    acc = load_startup()

    assert acc.city_map.entities[33].state['__class__'] == "ProductionFinishedState"

    u = open('pickup_production.json')
    data = json.load(u)
    map_(Account(), *data)

    assert acc.city_map.entities[33].state['__class__'] == "ProducingState"
    assert acc.city_map.entities[33].state['next_state_transition_at'] == 1639507690


def load_startup():
    f = open('startup.json')
    data = json.load(f)
    acc = map_(Account(), *data)
    return acc
