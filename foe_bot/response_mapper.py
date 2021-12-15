import logging

from domain.account import Account

__ignored = [
    'TrackingService.trackLoginDone',  # is done by login sequence via selenium webdriver
    'ResourceService.getPlayerAutoRefills'  # timestamps about last auto refilled resource, forge points for instance
]

logger = logging.getLogger("ResponseMapper")


def __map(acc: Account, **kwargs) -> None:
    if ('StartupService' == kwargs['requestClass'] and 'getData' == kwargs['requestMethod']):
        acc.city_user_data.__init__(**kwargs['responseData']['user_data'])
        acc.city_map.__init__(**kwargs['responseData']['city_map'])
        acc.socket_connection_parameter.__init__(**kwargs['responseData']['socket_connection_parameter'])
        acc.put_player(*kwargs['responseData']['socialbar_list'])

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

    elif 'HiddenRewardService' == kwargs['requestClass'] and 'getOverview' == kwargs['requestMethod']:
        acc.put_hidden_rewards(*kwargs['responseData']['hiddenRewards'])

    elif 'StaticDataService' == kwargs['requestClass'] and 'getMetadata' == kwargs['requestMethod']:
        acc.put_static_data(*kwargs['responseData'])

    else:
        class_method = f"{kwargs['requestClass']}.{kwargs['requestMethod']}"
        if class_method not in __ignored:
            logger.info(f"no mapping for {class_method}")


def map_to_account(acc: Account, *args) -> Account:
    for arg in args:
        __map(acc, **arg)
    return acc
