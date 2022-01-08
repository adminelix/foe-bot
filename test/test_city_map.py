import json

from cattr import structure

from foe_bot.domain.city_map import CityMap
from foe_bot.util import foe_json_loads


def test_process():
    f = open('test_data/startup.json')
    data = foe_json_loads(f.read())

    startup_service_data = json.dumps(data[30]['responseData']['city_map'])
    loads = foe_json_loads(startup_service_data)

    city = structure(loads, CityMap)

    assert city.gridId == 'main'
    assert len(city.entities) == 72
