import logging
import os
import pickle
import signal
import time

from domain.account import Account
from foe_bot import cfg
from foe_bot.city_production_service import CityProductionService
from foe_bot.hidden_reward_service import HiddenRewardService
from foe_bot.log_service import LogService
from foe_bot.other_player_service import OtherPlayerService
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account as map_
from foe_bot.static_data_service import StaticDataService

logger = logging.getLogger("app")
data_file = f"../data/{cfg['username']}_data"


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        logger.info("shutting down")
        self.kill_now = True


def load_account() -> Account:
    if os.path.isfile(data_file):
        with open(data_file, 'rb') as acc_file:
            return pickle.load(acc_file)
    else:
        return Account()


def save_account(acc: Account) -> None:
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    with open(data_file, 'wb') as acc_file:
        pickle.dump(acc, acc_file)


# TODO put ws_client into request and pickle request also and try to reuse session
# TODO simulate human play times
# TODO react on SIGINT and shutdown ws_client
def main():
    killer = GracefulKiller()
    acc = load_account()

    req = Request(acc)
    map_(acc, *req.initial_response)

    cps = CityProductionService(acc)
    hrs = HiddenRewardService(acc)
    ls = LogService(acc, req.ws_client)
    ops = OtherPlayerService(acc)
    StaticDataService(acc)

    while not killer.kill_now:
        ls.log_state()
        ls.log_performance_metrics()
        cps.pickup()
        cps.unlock_unit_slots()
        cps.produce()
        hrs.collect()
        ops.moppel()
        ops.accept_friend_invites()
        # ops.send_friend_invites() # TODO store invitation time to revert if not accepting after amount of time

        save_account(acc)
        if not killer.kill_now:
            time.sleep(10)

    req.ws_client.shutdown_flag.set()
    req.ws_client.join()
