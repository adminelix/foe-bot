import json
from datetime import datetime
from itertools import islice
from random import randint

import parsedatetime
from translate import Translator

from foe_bot import ARGS

global translator
cal = parsedatetime.Calendar()


def random_chunk(li, min_chunk=1, max_chunk=3):
    it = iter(li)
    while True:
        nxt = list(islice(it, randint(min_chunk, max_chunk)))
        if nxt:
            yield nxt
        else:
            break


def foe_json_loads(data: str):
    data = data.replace("__class__", "klass")
    return json.loads(data)


def parse_date(date: str) -> int:
    if 'translator' not in globals():
        translator = Translator(to_lang="en", from_lang='autodetect', provider='deepl',
                                secret_access_key=ARGS.deepl_api_key)

    translation = translator.translate(date)

    time_struct, parse_status = cal.parse(f"last {translation}")

    date_time = datetime(*time_struct[:6])
    time = int(date_time.timestamp())
    return time
