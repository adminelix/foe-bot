import logging.config
import sys

import configargparse

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
                    stream=sys.stdout)
logging.getLogger("seleniumwire.handler").setLevel(logging.WARN)
logging.getLogger("seleniumwire.server").setLevel(logging.WARN)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)

_args = lambda: None  # function as generic object() equivalent that can have attributes


def _str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise configargparse.ArgumentTypeError('Boolean value expected.')


parser = configargparse.ArgumentParser(
    prog="FoE-Bot",
    description="""
    A Forge of Empires bot that will do the annoying part of the game for you.
    """)

parser.add_argument('-u', '--username', type=str, nargs='?', required=True, env_var='FOE_BOT_USERNAME',
                    help='username of account')
parser.add_argument('-p', '--password', type=str, nargs='?', required=True, env_var='FOE_BOT_PASSWORD',
                    help='password to account')
parser.add_argument('-w', '--world', type=str, nargs='?', required=True, env_var='FOE_BOT_WORLD',
                    help="""world to play - Login into game via browser and look into the URL. It is the 'en11' of
                    'https://en11.forgeofempires.com/game/index'""")
parser.add_argument('-d', '--deepl-api-key', type=str, nargs='?', required=True, env_var='FOE_BOT_DEEPL_API_KEY',
                    help="""register on 'https://www.deepl.com/pro-api' and get the api key""")

general = parser.add_argument_group('general arguments (optional)', description='')
general.add_argument('--relog-waiting-time', type=int, nargs='?', required=False, env_var='FOE_BOT_RELOG_WAITING_TIME',
                     default=120, help="""wait time in seconds the bot will wait after you kick him out with
                     your login (default: 120)""")

other_player_service = parser.add_argument_group('other player (optional)', description='')
other_player_service.add_argument('--moppel', type=_str2bool, nargs='?', required=False, env_var='FOE_BOT_MOPPEL',
                                  default=True,
                                  help='moppel other players - friends, guild members and neighbours (default: true)')
other_player_service.add_argument('--manage-friends', type=_str2bool, nargs='?', required=False,
                                  env_var='FOE_BOT_MANAGE_FRIENDS', default=True,
                                  help="""accept and send friend invites and remove friends who do not support
                                  you in terms of moppeling you or visiting your friends tavern (default: true)""")

friends_tavern_service = parser.add_argument_group('friends tavern (optional)', description='')
friends_tavern_service.add_argument('--collect-tavern', type=_str2bool, nargs='?', required=False,
                                    env_var='FOE_BOT_COLLECT_TAVERN', default=True,
                                    help="""collect silver from own tavern if it is full (default: true)""")
friends_tavern_service.add_argument('--visit-tavern', type=_str2bool, nargs='?', required=False,
                                    env_var='FOE_BOT_VISIT_TAVERN', default=True,
                                    help="""visit taverns of all friends (default: true)""")
friends_tavern_service.add_argument('--upgrade-tavern', type=_str2bool, nargs='?', required=False,
                                    env_var='FOE_BOT_UPGRADE_TAVERN', default=True,
                                    help="""upgrade table, chairs and decorations of own tavern (default: true)""")

hidden_reward_service = parser.add_argument_group('hidden reward (optional)', description='')
hidden_reward_service.add_argument('--collect-hidden-rewards', type=_str2bool, nargs='?', required=False,
                                   env_var='FOE_BOT_COLLECT_HIDDEN_REWARDS', default=True,
                                   help="""gather hidden rewards on city map (default: true)""")

city_production_service = parser.add_argument_group('city production (optional)', description='')
city_production_service.add_argument('--pickup-city-production', type=_str2bool, nargs='?', required=False,
                                     env_var='FOE_BOT_PICKUP_CITY_PRODUCTION', default=True,
                                     help="""pickup city buildings (default: true)""")
city_production_service.add_argument('--start-city-production', type=_str2bool, nargs='?', required=False,
                                     env_var='FOE_BOT_START_CITY_PRODUCTION', default=True,
                                     help="""start production of buildings (default: true)""")
city_production_service.add_argument('--unlock-unit-slots', type=_str2bool, nargs='?', required=False,
                                     env_var='FOE_BOT_UNLOCK_UNIT_SLOTS', default=True,
                                     help="""unlock unit slots in military buildings (default: true)""")

city_production_service = parser.add_argument_group('sniping (optional)', description='')
city_production_service.add_argument('--auto-snipe-neighbours', type=_str2bool, nargs='?', required=False,
                                     env_var='FOE_BOT_AUTO_SNIPE_NEIGHBOURS', default=True,
                                     help="""scan and snipe neighbours automatically (default: true)""")
city_production_service.add_argument('--players-to-snipe', type=str, nargs='?', required=False,
                                     env_var='FOE_BOT_PLAYERS_TO_SNIPE', default="",
                                     help="""scan defined players (case-sensitive) and notify if a great building is
                                     able to snipe (sample: "foo, bar")""")


def parse_args():
    global _args
    _args = parser.parse_args()


def get_args():
    return _args
