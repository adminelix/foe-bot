import json

from domain.city_user_data import CityUserData


def test_process():
    f = open('content.json')
    data = json.load(f)

    startup_service_data = json.dumps(data[30]['responseData']['user_data'])
    loads = json.loads(startup_service_data)

    cud = CityUserData(**loads)

    assert cud.player_id == 8365227

