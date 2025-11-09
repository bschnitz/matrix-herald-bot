class ConfigurationError(Exception):
    pass

class Configuration:
    def __init__(
        self,
        homeserver: str,
        server_admin_id: str,
        server_admin_token: str,
        announcement_room: str,
        watched_spaces: list[str]
    ):
        self.homeserver = homeserver
        self.server_admin_id = server_admin_id
        self.server_admin_token = server_admin_token
        self.announcement_room = announcement_room
        self.watched_spaces = watched_spaces
