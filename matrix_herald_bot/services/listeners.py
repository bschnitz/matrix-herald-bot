import sys
import inspect
from injector import Injector, Module, inject, multiprovider, singleton
from nio import Event, MatrixRoom, RoomSpaceChildEvent, UnknownEvent
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.core.event.bus import EventBus
from matrix_herald_bot.core.event.events import TreeStructureUpdated
from matrix_herald_bot.services.action_service import MatrixActionService
from matrix_herald_bot.services.admin_service import TuwunelAdminService
from matrix_herald_bot.services.tree_cache import MatrixTreeCache
from matrix_herald_bot.services.tree_operations import MatrixTreeOperations
from matrix_herald_bot.services.tree_builder import MatrixTreeBuilder

class ListenerInterface[T: Event]:
    def getEventType(self) -> type[T]:
        raise NotImplementedError

    async def onEvent(self, room: MatrixRoom, event: T):
        raise NotImplementedError

@singleton
class UpdateWatchedTreeOnSpaceChildAdded(ListenerInterface[RoomSpaceChildEvent]):
    @inject
    def __init__(
        self,
        tree_cache: MatrixTreeCache,
        tree_builder: MatrixTreeBuilder,
        tree_operations: MatrixTreeOperations,
        admin_service: TuwunelAdminService,
        action_service: MatrixActionService,
        config: Configuration,
        event_bus: EventBus
    ):
        self.tree_cache = tree_cache
        self.tree_builder = tree_builder
        self.admin_service = admin_service
        self.action_service = action_service
        self.tree_operations = tree_operations
        self.config = config
        self.event_bus = event_bus

    def getEventType(self) -> type[RoomSpaceChildEvent]:
        return RoomSpaceChildEvent

    async def onEvent(self, room: MatrixRoom, event: RoomSpaceChildEvent):
        watched_space = self.config.watched_space
        current_tree = self.tree_cache[watched_space]
        if room in current_tree.child_ids:
            tree = (await self.tree_operations
                              .fetch_tree_and_join_on_all_public_nodes(watched_space))
            self.tree_cache[watched_space] = tree
            await self.event_bus.publish(TreeStructureUpdated(tree))

@singleton
class RespondOnTreeRequest(ListenerInterface[UnknownEvent]):
    @inject
    def __init__(
        self,
        tree_builder: MatrixTreeBuilder,
        tree_operations: MatrixTreeOperations,
        config: Configuration,
    ):
        self.config = config
        self.tree_builder = tree_builder
        self.tree_operations = tree_operations

    def getEventType(self) -> type[UnknownEvent]:
        return UnknownEvent

    async def onEvent(self, room: MatrixRoom, event: UnknownEvent):
        if event.type == 'org.herald.tree_structure_request':
            print("Sending tree to widget.")
            tree = await self.tree_builder.fetch_tree(self.config.watched_space)
            await self.tree_operations.send_tree_to_room(tree, room.room_id)

class MatrixListenerCollectionModule(Module):
    @multiprovider
    def provide_listeners(self, injector: Injector) -> list[ListenerInterface]:
        current_module = sys.modules[__name__]

        listeners = []

        for name, obj in inspect.getmembers(current_module, inspect.isclass):
            if not issubclass(obj, ListenerInterface):
                continue

            if obj is ListenerInterface:
                continue

            listeners.append(injector.get(obj))

        return listeners
