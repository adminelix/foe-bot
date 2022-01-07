import logging
import signal
import time

from foe_bot.foe_client.client import Client
from foe_bot.service.abstract_service import AbstractService
from foe_bot.service.account_service import AccountService
from foe_bot.service import *

logger = logging.getLogger("app")


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        # signal.signal(signal.SIGKILL, sys.exit())

    def exit_gracefully(self, *args):
        logger.info("shutting down")
        self.kill_now = True


def list_services():
    services = []
    for subclass in AbstractService.__subclasses__():
        services.append(subclass())
    return services


def main():
    killer = GracefulKiller()
    services = list_services()
    client = Client()

    while not killer.kill_now:
        for service in services:
            if not killer.kill_now and client.is_connected:
                service.do()
            elif not client.is_connected:
                client.relog_in()

        time.sleep(0.5)

    AccountService().save()
    client.tear_down()
    client.save_session()
