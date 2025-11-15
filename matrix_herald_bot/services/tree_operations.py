from injector import inject, singleton
from nio import RoomPutStateError, RoomPutStateResponse
from matrix_herald_bot.model.tree import MatrixTree, MatrixTreeNode
from matrix_herald_bot.services.admin_service import TuwunelAdminService
from matrix_herald_bot.util.tree_iterator import MatrixTreeIterator
from matrix_herald_bot.services.action_service import MatrixActionService
from matrix_herald_bot.services.tree_builder import MatrixTreeBuilder

@singleton
class MatrixTreeOperations:
    @inject
    def __init__(
        self,
        admin_service: TuwunelAdminService,
        action_service: MatrixActionService,
        tree_builder: MatrixTreeBuilder
    ):
        self.admin_service = admin_service
        self.action_service = action_service
        self.tree_builder = tree_builder

    async def fetch_tree_and_join_on_all_public_nodes(self, room_id: str) -> MatrixTree:
        async def join_room(room_id: str):
            await self.action_service.join_room(room_id)

        return await self.tree_builder.fetch_tree(room_id, join_room)

    async def join_and_promote_users_on_all_public_nodes(
        self,
        room_id: str,
        users: list[str]
    ) -> MatrixTree:
        async def join_room(room_id: str):
            await self.action_service.join_room(room_id)

        tree = await self.tree_builder.fetch_tree(room_id, join_room)

        for node in MatrixTreeIterator(tree.root):
            if node.public:
                print(node.name)
                await self.admin_service.force_promote_users(users, node.id)

        return tree

    async def send_tree_to_room(
        self,
        tree: MatrixTree,
        room_id: str,
    ) -> RoomPutStateResponse|RoomPutStateError:
        return await self.action_service.room_put_state(
            room_id,
            'org.herald.tree_structure',
            tree.convert_to_dict(),
            'herald_widget'
        )
