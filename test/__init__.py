import os

from foe_bot import _args


def get_env_or_raise(name: str) -> str:
    env_var = os.getenv(name)
    if not env_var:
        raise AttributeError(f"environment variable {name} not set")
    return env_var


def set_args():
    _args.__setattr__('username', get_env_or_raise("FOE_BOT_USERNAME"))
    _args.__setattr__('password', get_env_or_raise("FOE_BOT_PASSWORD"))
    _args.__setattr__('world', get_env_or_raise("FOE_BOT_WORLD"))
    _args.__setattr__('deepl_api_key', get_env_or_raise("FOE_BOT_DEEPL_API_KEY"))
