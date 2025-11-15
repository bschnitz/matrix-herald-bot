import logging
from aiohttp import ClientSession
from injector import inject, singleton
from nio import RoomGetStateError, RoomPutStateError
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.connection.connection import Connection
from matrix_herald_bot.core.event.bus import EventBus
from matrix_herald_bot.core.event.listener_interface import CoreListenerInterface
from matrix_herald_bot.core.logging.loggers import CoreLogger, MatrixLogger
from matrix_herald_bot.services.tree_builder import MatrixTreeBuilder
from matrix_herald_bot.services.tree_printer import MatrixTreePrinter
from matrix_herald_bot.services.admin_service import TuwunelAdminService
from matrix_herald_bot.services.action_service import MatrixActionService
from matrix_herald_bot.services.tree_operations import MatrixTreeOperations
from matrix_herald_bot.services.notification_service import NotificationService
from matrix_herald_bot.services.listeners import ListenerInterface

@singleton
class PrintMatrixTreesOfWatchedSpaceCmd:
    @inject
    def __init__(
        self,
        config: Configuration,
        connection: Connection,
        tree_builder: MatrixTreeBuilder,
        tree_printer: MatrixTreePrinter,
        logger: MatrixLogger
    ):
        self.config = config
        self.connection = connection
        self.tree_builder = tree_builder
        self.tree_printer = tree_printer
        self.logger = logger

    async def print_tree(self):
        await self.connection.connect()
        tree = await self.tree_builder.fetch_tree(self.config.watched_space)
        self.tree_printer.print_matrix_tree(tree.root)
        print("\n" + "=" * 40 + "\n")
        await self.connection.close()

@singleton
class PromoteToServerAdmin:
    @inject
    def __init__(
        self,
        config: Configuration,
        connection: Connection,
        admin_service: TuwunelAdminService
    ):
        self.config = config
        self.connection = connection
        self.admin_service = admin_service

    async def promote_to_server_admin(self, user_id: str):
        await self.connection.connect()
        resp = await self.admin_service.make_user_admin(user_id)
        await self.connection.close()
        return resp

@singleton
class PrintUsersInAnnouncementRoom:
    @inject
    def __init__(
        self,
        connection: Connection,
        action_service: MatrixActionService
    ):
        self.connection = connection
        self.action_service = action_service

    async def print_users_in_announcement_room(self):
        await self.connection.connect()
        print(await self.action_service.get_users_in_announcement_room())
        await self.connection.close()

@singleton
class PromoteUsersInAnnouncementRoom:
    """
    Promotes the users in the announcement room to be admin in all watched
    spaces and their subspaces and rooms recursively.
    """
    @inject
    def __init__(
        self,
        config: Configuration,
        connection: Connection,
        action_service: MatrixActionService,
        tree_builder: MatrixTreeBuilder,
        tree_operations: MatrixTreeOperations,
    ):
        self.config = config
        self.connection = connection
        self.tree_builder = tree_builder
        self.action_service = action_service
        self.tree_operations = tree_operations

    async def promote_users_in_announcement_room(self):
        await self.connection.connect()

        print(
            "Promoting the users in the announcement room to be admin in all "+
            "watched spaces, their subspaces and room recursively."
        )

        users = await self.action_service.get_users_in_announcement_room()
        if isinstance(users, RoomGetStateError):
            print(f"Error fetching users in announcement room: {users}")
            return

        print(f"Users for promotion: {users}")
        print(f"Rercursivly promoting users in {self.config.watched_space}")
        await self.tree_operations.join_and_promote_users_on_all_public_nodes(
            self.config.watched_space,
            users
        )

        await self.connection.close()

@singleton
class SendTreeToWidget:
    @inject
    def __init__(
        self,
        config: Configuration,
        connection: Connection,
        action_service: MatrixActionService,
        tree_builder: MatrixTreeBuilder,
        tree_operations: MatrixTreeOperations,
    ):
        self.config = config
        self.connection = connection
        self.tree_builder = tree_builder
        self.action_service = action_service
        self.tree_operations = tree_operations

    async def send_tree_to_widget(self, room_id: str):
        await self.connection.connect()

        room = self.config.watched_space
        tree = await self.tree_builder.fetch_tree(room)
        response = await self.tree_operations.send_tree_to_room(
            tree.root,
            room_id,
            "org.herald.tree_structure"
        )
        if isinstance(response, RoomPutStateError):
            print(f"Fehler beim Senden: {response.message}")
        else:
            print(f"Tree-Struktur gesendet: {response.event_id}")

        await self.connection.close()

@singleton
class PrintUnreadNotifications:
    @inject
    def __init__(
        self,
        connection: Connection,
        notification_service: NotificationService
    ):
        self.connection = connection
        self.notification_service = notification_service

    async def print_all_unread_notifications(self):
        await self.connection.connect()
        unread_notifications = await self.notification_service.get_all_unread_notifications()
        print(unread_notifications)
        await self.connection.close()

@singleton
class PrintAllUnreadNotifications:
    @inject
    def __init__(
        self,
        connection: Connection,
        config: Configuration
    ):
        self.config = config
        self.connection = connection

    async def print_all_unread_notifications(self):
        await self.connection.connect()
        url = f"{self.config.homeserver}/_matrix/client/v3/notifications"
        headers = {"Authorization": f"Bearer {self.config.server_admin_token}"}

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                notifications = data.get("notifications", [])

                print(f"Found {len(notifications)} notifications\n")
                for n in notifications:
                    room = n.get("room_id")
                    event_id = n.get("event_id")
                    type_ = n.get("type")
                    highlight = n.get("highlight")
                    print(f"Room: {room}, Event: {event_id}, Type: {type_}, Highlight: {highlight}")
                await self.connection.close()

@singleton
class HeraldBotEventLoop:
    @inject
    def __init__(
        self,
        connection: Connection,
        listeners: list[ListenerInterface],
        logger: CoreLogger
    ):
        self.connection = connection
        self.listeners = listeners
        self.logger = logger

    async def start(self):
        """Connects to Matrix and runs the bot event loop."""
        self.logger.info("Starting Herald main event loop.")
        await self.connection.connect()

        async with self.connection as c:
            client = c.get_client_or_raise()
            for listener in self.listeners:
                client.add_event_callback(listener.onEvent, listener.getEventType())

            await client.sync_forever(timeout=3000, full_state=True)
