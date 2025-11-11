from injector import inject, singleton
from nio import RoomSendError, RoomSendResponse
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.connection.connection import Connection

@singleton
class TuwunelAdminService:
    """Provides administrative Matrix operations (power levels, invites, etc.)."""

    @inject
    def __init__(self, config: Configuration, connection: Connection):
        self.config = config
        self.connection = connection

    async def _send_admin_command(self, command: str) -> RoomSendResponse|RoomSendError:
        """Send a command to the admin room."""
        client = self.connection.get_client_or_raise()

        resp = await client.room_send(
            room_id=self.config.admin_room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": command}
        )
        return resp

    async def force_promote(self, user_id: str, room_id: str):
        cmd = f"!admin users force-promote {user_id} {room_id}"
        return await self._send_admin_command(cmd)

    async def force_promote_users(self, users: list[str], room_id: str):
        for user in users:
            await self.force_promote(user, room_id)

    async def force_join_room(self, user_id: str, room_id: str):
        cmd = f"!admin users force-join-room {user_id} {room_id}"
        return await self._send_admin_command(cmd)

    async def make_user_admin(self, user_id: str):
        cmd = f"!admin users make-user-admin {user_id}"
        return await self._send_admin_command(cmd)
