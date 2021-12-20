from datetime import datetime

from foe_bot.static_data_service import StaticDataService
from foe_bot.util import parse_date, cal
from test.test_response_mapper import load_startup


def test_find_unit_in_city_entities():
    acc = load_startup()

    sds = StaticDataService(acc)
    unit = sds.find_available_products_in_city_entities('M_BronzeAge_ArcheryRange')[0]
    assert unit['unit_type_id'] == 'slinger'


def test_product_in_city_entities():
    acc = load_startup()

    sds = StaticDataService(acc)
    product = sds.find_available_products_in_city_entities('G_BronzeAge_IndigoPlantation')[0]
    assert product['deposit_id'] == 'raw_dye'


def test_print_all_goods():
    acc = load_startup()

    sds = StaticDataService(acc)
    data = sds.get_data('city_entities')

    goods = set([a['available_products'][0]['deposit_id'] for a in data if 'type' in a.keys()
                 and a['type'] == 'goods'
                 and 'deposit_id' in a['available_products'][0].keys()])
    print(f"all goods in game: {goods}")


def test_time_parsing():
    time_struct, parse_status = cal.parse("last yesterday at 8:00")
    foo = datetime(*time_struct[:6])
    expected = int(foo.timestamp())

    current = parse_date("gestern um 8:00")

    assert expected == current


def test_doo():
    x = 1
    if x > None:
        pass
