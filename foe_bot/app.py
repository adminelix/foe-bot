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
from foe_bot.ws_client import WsClient

logger = logging.getLogger("app")
data_file = f"../data/{cfg['username']}_data"
session_file = f"../data/{cfg['username']}_session"


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


def load_session() -> Request:
    if os.path.isfile(session_file):
        with open(session_file, 'rb') as req_file:
            req = pickle.load(req_file)
            foo = Request(**req.__dict__)
            return foo
    else:
        return Request()


def save_session(req: Request) -> None:
    os.makedirs(os.path.dirname(session_file), exist_ok=True)
    with open(session_file, 'wb') as req_file:
        pickle.dump(req, req_file)


# TODO put ws_client into request and pickle request also and try to reuse session
# TODO simulate human play times
# TODO react on SIGINT and shutdown ws_client
def main():
    killer = GracefulKiller()
    acc = load_account()

    req = load_session()
    map_(acc, *req.initial_response)
    req.initial_response = []
    ws_client = WsClient(acc)
    ws_client.start()

    time.sleep(1)
    ws_client = relog_if_needed(acc, req, ws_client, 0)

    cps = CityProductionService(acc)
    hrs = HiddenRewardService(acc)
    ls = LogService(acc, ws_client)
    ops = OtherPlayerService(acc)
    StaticDataService(acc)

    while not killer.kill_now:
        ws_client = relog_if_needed(acc, req, ws_client, cfg['relog_leeway'])
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
        save_session(req)
        if not killer.kill_now:
            time.sleep(10)

    ws_client.shutdown_flag.set()
    ws_client.join()


def relog_if_needed(acc, req, ws_client, wait):
    if not ws_client.is_alive():
        if wait > 0:
            logger.info(f"session expired, relog in {wait}s")
            time.sleep(wait)
        req.login()
        ws_client = WsClient(acc)
        ws_client.start()
    return ws_client
