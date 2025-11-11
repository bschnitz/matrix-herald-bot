from dataclasses import dataclass
from injector import inject, singleton
from nio import SyncError

from matrix_herald_bot.connection.connection import Connection

@dataclass
class UnreadRoomNotifications:
    room_id: str
    notification_count: int|None
    highlight_count: int|None

@singleton
class NotificationService:
    @inject
    def __init__(self, connection: Connection):
        self.connection = connection

    async def get_all_unread_notifications(self) -> SyncError|list[UnreadRoomNotifications]:
        sync_response = await self.connection.get_client_or_raise().sync(5000)

        if isinstance(sync_response, SyncError):
            return sync_response

        unread_notifications = []

        for room_id, room_data in sync_response.rooms.join.items():

            if (
                ((ur := room_data.unread_notifications) is not None)
                and
                ((ur.notification_count or 0) > 0 or (ur.highlight_count or 0) > 0)
            ):
                unread_notifications.append(UnreadRoomNotifications(
                    room_id,
                    ur.notification_count,
                    ur.highlight_count
                ))

        return unread_notifications
