import re
import sys


def test_gather():
    # TODO mock Request() in CityProductionService() and test filter
    pass


def test_foo():
    bar: str = "nrerfv12"
    foo = re.sub(r'[a-zA-Z]', '', bar)

    print(foo)
    sys.stderr.write(foo)
