import os

from foe_bot.domain.account import Account
from foe_bot.domain.city_map_entity import CityMapEntity
from foe_bot.foe_client.response_mapper import map_to_account as map_
from foe_bot.util import foe_json_loads


def test_startup():
    acc = load_startup()
    assert len(acc.city_map.entities) == 113
    assert acc.city_map.entities.get(140).type == 'street'
    assert acc.resources.supplies == 255268
    assert len(acc.players) == 86
    assert acc.city_user_data.player_id == 8365227


def test_start_production():
    acc = load_startup()

    ent: CityMapEntity = acc.city_map.entities[212]
    assert ent.state.klass == "ProductionFinishedState"

    u = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/start_production_response.json")
    data = foe_json_loads(u.read())

    map_(acc, *data)

    ent = acc.city_map.entities[212]
    assert ent.state.klass == "ProducingState"


def test_pickup_production():
    acc = load_startup()

    assert acc.city_map.entities[252].state.klass == "ProductionFinishedState"

    u = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/pickup_production_response.json")
    data = foe_json_loads(u.read())
    map_(acc, *data)

    assert acc.city_map.entities[252].state.klass == "ProducingState"
    assert acc.city_map.entities[252].state.next_state_transition_at == 1643034341


def test_unlock_chair():
    acc = load_startup()

    u = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/unlock_chair_response.json")
    data = foe_json_loads(u.read())
    map_(acc, *data)

    assert acc.own_tavern.view.unlockedChairs == 5


def test_unlock_table():
    acc = load_startup()

    u = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/unlock_table_response.json")
    data = foe_json_loads(u.read())
    map_(acc, *data)

    assert acc.own_tavern.view.tableLevel == 2


def test_unlock_customization():
    acc = load_startup()

    u = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/unlock_customization_response.json")
    data = foe_json_loads(u.read())
    map_(acc, *data)

    assert len(acc.own_tavern.unlockedCustomizationIds) == 4
    assert 'tray_1' in acc.own_tavern.unlockedCustomizationIds


def test_hidden_reward_overview_get_overview_response():
    u = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/hidden_reward_overview-get_overview-response.json")
    data = foe_json_loads(u.read())
    map_(Account(), *data)


def load_startup():
    f = open(f"{os.path.dirname(os.path.realpath(__file__))}/test_data/startup.json")
    data = foe_json_loads(f.read())
    acc = map_(Account(), *data)
    return acc
