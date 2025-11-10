from injector import inject, singleton
from nio import RoomGetStateError, RoomPutStateError
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.connection.connection import Connection
from matrix_herald_bot.services.tree_builder import MatrixTreeBuilder
from matrix_herald_bot.services.tree_printer import MatrixTreePrinter
from matrix_herald_bot.services.admin_service import TuwunelAdminService
from matrix_herald_bot.services.action_service import MatrixActionService
from matrix_herald_bot.services.tree_operations import MatrixTreeOperations

@singleton
class PrintMatrixTreesOfWatchedSpacesCmd:
    @inject
    def __init__(
        self,
        config: Configuration,
        connection: Connection,
        tree_builder: MatrixTreeBuilder,
        tree_printer: MatrixTreePrinter
    ):
        self.config = config
        self.connection = connection
        self.tree_builder = tree_builder
        self.tree_printer = tree_printer

    async def print_trees(self):
        await self.connection.connect()
        for space_id in self.config.watched_spaces:
            root_node = await self.tree_builder.fetch_tree(space_id)
            self.tree_printer.print_matrix_tree(root_node)
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
        for room in self.config.watched_spaces:
            root = await self.tree_builder.fetch_tree(room)
            print(f"Rercursivly promoting users in {root.name}")
            await self.tree_operations.promote_users_on_all_public_nodes(root, users)

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

        room = self.config.watched_spaces[0]
        root = await self.tree_builder.fetch_tree(room)
        response = await self.tree_operations.send_tree_to_room(
            root,
            room_id,
            "org.herald.tree_structure"
        )
        if isinstance(response, RoomPutStateError):
            print(f"Fehler beim Senden: {response.message}")
        else:
            print(f"Tree-Struktur gesendet: {response.event_id}")

        await self.connection.close()
