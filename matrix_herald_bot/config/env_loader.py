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
    watched_spaces_raw = getenv_or_raise("WATCHED_SPACES")
    watched_spaces = [item.strip() for item in watched_spaces_raw.split(",") if item.strip()]
    return Configuration(
        homeserver=getenv_or_raise("HOMESERVER"),
        server_admin_id=getenv_or_raise("SERVER_ADMIN_ID"),
        server_admin_token=getenv_or_raise("SERVER_ADMIN_TOKEN"),
        announcement_room=getenv_or_raise("ANNOUNCEMENT_ROOM"),
        watched_spaces=watched_spaces
    )
