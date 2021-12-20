from datetime import datetime

import parsedatetime

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


def test_bla():
    acc = load_startup()

    sds = StaticDataService(acc)
    data = sds.get_data('city_entities')

    filt = set([a['available_products'][0]['deposit_id'] for a in data if 'type' in a.keys()
                and a['type'] == 'goods'
                and 'deposit_id' in a['available_products'][0].keys()])
    pass


def test_foo():
    cal = parsedatetime.Calendar()

    time_struct, parse_status = cal.parse("last yesterday at 8:00")

    foo = datetime(*time_struct[:6])
    time = int(foo.timestamp())
    pass


def test_foobar():
    from translate import Translator
    translator = Translator(to_lang="en", provider='mymemory', from_lang='autodetect')
    translation = translator.translate("gestern um 8:00")
    pass
