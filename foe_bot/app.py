import logging
import os
import pickle
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
filename = f"../data/{cfg[0]['username']}_data"


def load_account() -> Account:
    if os.path.isfile(filename):
        with open(filename, 'rb') as acc_file:
            return pickle.load(acc_file)
    else:
        return Account()


def save_account(acc: Account) -> None:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as acc_file:
        pickle.dump(acc, acc_file)

# TODO put ws_client into request and pickle request also and try to reuse session
# TODO simulate human play times
# TODO react on SIGINT and shutdown ws_client
def main():
    acc = load_account()

    req = Request()
    map_(acc, *req.initial_response)

    token = req._session.cookies['socket_token']
    url = req._session.cookies['socketGatewayUrl']
    ws_client = WsClient(acc, url, token)
    ws_client.run()

    cps = CityProductionService(acc)
    hrs = HiddenRewardService(acc)
    ls = LogService(acc, ws_client)
    ops = OtherPlayerService(acc)
    StaticDataService(acc)

    while True:
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
        time.sleep(10)

    ws_client.stop()
