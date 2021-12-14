from domain.account import Account

__ignored = ['TrackingService.trackLoginDone']


def __map(acc: Account, **kwargs) -> None:
    if ('StartupService' == kwargs['requestClass'] and 'getData' == kwargs['requestMethod']):
        acc.city_user_data.__init__(**kwargs['responseData']['user_data'])
        acc.city_map.__init__(**kwargs['responseData']['city_map'])
        acc.socket_connection_parameter.__init__(**kwargs['responseData']['socket_connection_parameter'])

    elif 'TimeService' == kwargs['requestClass'] and 'updateTime' == kwargs['requestMethod']:
        acc.time.__init__(**kwargs['responseData'])

    elif 'LogService' == kwargs['requestClass'] and 'setLogState' == kwargs['requestMethod']:
        acc.connection_state_logging.__init__(**kwargs['responseData'])

    elif ('CityProductionService' == kwargs['requestClass']
          and ('startProduction' == kwargs['requestMethod']
               or 'pickupProduction' == kwargs['requestMethod'])):
        acc.city_map.put_entities(*kwargs['responseData']['updatedEntities'])

    elif 'ResourceService' == kwargs['requestClass'] and 'getPlayerResources' == kwargs['requestMethod']:
        acc.resources.__init__(**kwargs['responseData']['resources'])

    else:
        class_method = f"{kwargs['requestClass']}.{kwargs['requestMethod']}"
        if class_method not in __ignored:
            print(f"no mapping for {class_method}")


def map_to_account(acc: Account, *args) -> Account:
    for arg in args:
        __map(acc, **arg)
    return acc
