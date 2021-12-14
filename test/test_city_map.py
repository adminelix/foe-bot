import json

from domain.city_map import CityMap


def test_process():
    f = open('startup.json')
    data = json.load(f)

    startup_service_data = json.dumps(data[30]['responseData']['city_map'])
    loads = json.loads(startup_service_data)

    city = CityMap(**loads)

    assert city.gridId == 'main'
    assert city.entities[1].type == 'main_building'
