from injector import inject, singleton
from nio import JoinError, JoinResponse, RoomGetStateError, RoomPutStateError, RoomPutStateResponse
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.connection.connection import Connection
from matrix_herald_bot.util.exceptions import NioErrorResponseException

@singleton
class MatrixActionService:
    """Provides regular Matrix actions."""

    @inject
    def __init__(self, connection: Connection, config: Configuration):
        self.config = config
        self.connection = connection

    async def join_room(self, room_id: str) -> JoinResponse | JoinError:
        client = self.connection.get_client_or_raise()
        response = await client.join(room_id)
        return response

    async def get_users_in_room(self, room_id: str) -> list[str]|RoomGetStateError:
        client = self.connection.get_client_or_raise()
        state = await client.room_get_state(room_id)

        if isinstance(state, RoomGetStateError):
            return state

        return [
            ev["state_key"]
            for ev in state.events
            if ev["type"] == "m.room.member" and ev.get("content", {}).get("membership") == "join"
        ]

    async def get_users_in_announcement_room(self) -> list[str]|RoomGetStateError:
        return await self.get_users_in_room(self.config.announcement_room)

    async def get_users_in_announcement_room_or_raise(self) -> list[str]:
        resp = await self.get_users_in_room(self.config.announcement_room)
        if isinstance(resp, RoomGetStateError):
            raise NioErrorResponseException(resp)
        return resp

    async def room_put_state(
        self,
        room_id: str,
        event_type: str,
        content: dict,
        state_key=""
    ) -> RoomPutStateResponse|RoomPutStateError:
        client = self.connection.get_client_or_raise()

        return await client.room_put_state(
            room_id,
            event_type,
            content,
            state_key
        )
