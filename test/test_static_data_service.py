from foe_bot.static_data_service import StaticDataService
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
