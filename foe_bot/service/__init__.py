__all__ = [
    "abstract_service",
    "city_production_service",
    "friends_tavern_service",
    "hidden_reward_service",
    "other_player_service",
    "static_data_service",
    "sniping_service"
]

import requests

from foe_bot import get_args


def telegram_send(text):
    token = get_args().telegram_token
    chat_id = get_args().telegram_chat_id
    if token and chat_id:
        requests.post(url=f"https://api.telegram.org/bot{token}/sendMessage",
                      data={"chat_id": chat_id, "text": text})
