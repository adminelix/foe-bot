from domain.account import Account


def __map(acc: Account, **kwargs) -> None:
    if 'Startup' == kwargs['__class__']:
        acc.city_user_data.__init__(**kwargs['user_data'])
        acc.city_map.__init__(**kwargs['city_map'])
        acc.socket_connection_parameter.__init__(**kwargs['socket_connection_parameter'])
    elif 'Time' == kwargs['__class__']:
        acc.time.__init__(**kwargs)


def map(acc: Account, *args) -> Account:
    for arg in args:
        if type(arg['responseData']) == list:
            for data in arg['responseData']:
                if type(data) == dict:
                    __map(acc, **data)
        elif type(arg['responseData']) == dict:
            if arg['responseData']['__class__']:
                __map(acc, **arg['responseData'])
            else:
                for item in arg['responseData']:
                    __map(acc, **item)
        else:
            print('cannot handle: ' + repr(arg))
    return acc
