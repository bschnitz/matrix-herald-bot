import os
from dotenv import load_dotenv

from matrix_herald_bot.config.model import Configuration, ConfigurationError

def getenv_or_raise(varname: str) -> str:
    value = os.getenv(varname)
    if not value or not value.strip():
        raise ConfigurationError(f"Environment variable '{varname}' is missing or empty.")
    return value

def build_configuration_from_env() -> Configuration:
    load_dotenv()
    config = Configuration(
        getenv_or_raise("HOMESERVER"),
        getenv_or_raise("SERVER_ADMIN_ID"),
        getenv_or_raise("SERVER_ADMIN_TOKEN"),
        getenv_or_raise("ANNOUNCEMENT_ROOM"),
        getenv_or_raise("WATCHED_SPACE"),
        getenv_or_raise("ADMIN_ROOM_ID"),
        getenv_or_raise("ENVIRONMENT"),
    )
    return config
