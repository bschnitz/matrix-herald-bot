import sys
import inspect
import asyncio
from injector import Injector, Module, inject, multiprovider, singleton
from nio import RoomPutStateError, RoomPutStateResponse
from matrix_herald_bot.core.event.events import TreeStructureUpdated
from matrix_herald_bot.core.event.listener_interface import CoreListenerInterface
from matrix_herald_bot.services.action_service import MatrixActionService
from matrix_herald_bot.services.admin_service import TuwunelAdminService
from matrix_herald_bot.services.tree_operations import MatrixTreeOperations

@singleton
class UpdateHeraldWidgetsOnTreeStructureUpdate(CoreListenerInterface[TreeStructureUpdated]):
    @inject
    def __init__(self, tree_operations: MatrixTreeOperations):
        self.tree_operations = tree_operations

    def getEventType(self) -> type[TreeStructureUpdated]:
        return TreeStructureUpdated

    async def onEvent(
        self,
        event: TreeStructureUpdated
    ) -> list[RoomPutStateResponse|RoomPutStateError]:
        tasks = [
            self.tree_operations.send_tree_to_room(event.tree, widget.room_id)
            for widget in event.tree.herald_widgets
        ]
        return await asyncio.gather(*tasks)

@singleton
class PromoteUsersOnTreeStructureUpdate(CoreListenerInterface[TreeStructureUpdated]):
    def __init__(
        self,
        admin_service: TuwunelAdminService,
        action_service: MatrixActionService
    ):
        self.admin_service = admin_service
        self.action_service = action_service

    def getEventType(self) -> type[TreeStructureUpdated]:
        return TreeStructureUpdated

    async def onEvent(self, event: TreeStructureUpdated):
        users = await self.action_service.get_users_in_announcement_room_or_raise()
        rooms = event.tree.child_ids
        await self.admin_service.force_promote_users_in_rooms(users, rooms)

class InternalListenerCollectionModule(Module):
    @multiprovider
    def provide_listeners(self, injector: Injector) -> list[CoreListenerInterface]:
        current_module = sys.modules[__name__]

        listeners = []

        for name, obj in inspect.getmembers(current_module, inspect.isclass):
            if not issubclass(obj, CoreListenerInterface):
                continue

            if obj is CoreListenerInterface:
                continue

            listeners.append(injector.get(obj))

        return listeners
