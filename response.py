from persistent.model import Model


def process(*args):
    for arg in args:
        bar(args)


def bar(**kwargs):
    bla = Model.__subclasses__()
    gen = (subclass for subclass in Model.__subclasses__() if subclass.__tablename__ == food)
    subclass = next(gen, None)
    if subclass is None:
        raise ValueError("No animal eats " + repr(food))
    new_obj = subclass()


def test_process():
    assert True
