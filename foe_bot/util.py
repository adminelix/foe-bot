import json
from itertools import islice
from random import randint


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
