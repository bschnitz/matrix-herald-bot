from injector import inject, singleton
from nio import AsyncClient
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.model.exceptions import NotConnectedError

@singleton
class Connection:
    @inject
    def __init__(self, config: Configuration):
        self.config = config
        self.client: AsyncClient | None = None
        self.connected = False

    async def connect(self):
        client = AsyncClient(self.config.homeserver, self.config.server_admin_id)
        client.access_token = self.config.server_admin_token
        client.user_id = self.config.server_admin_id
        self.client = client
        self.connected = True

    def get_client(self) -> AsyncClient | None:
        return self.client

    def get_client_or_raise(self) -> AsyncClient:
        if self.client is None:
            raise NotConnectedError

        return self.client

    async def close(self):
        if self.client:
            await self.client.close()
