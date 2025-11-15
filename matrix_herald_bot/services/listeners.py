import sys
import inspect
from injector import Injector, Module, inject, multiprovider, singleton
from nio import Event, MatrixRoom, RoomSpaceChildEvent, UnknownEvent
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.core.event.bus import EventBus
from matrix_herald_bot.core.event.events import TreeStructureUpdated
from matrix_herald_bot.core.logging.loggers import MatrixLogger
from matrix_herald_bot.services.action_service import MatrixActionService
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
        tree_operations: MatrixTreeOperations,
        config: Configuration,
        event_bus: EventBus,
        logger: MatrixLogger,
        action_service: MatrixActionService
    ):
        self.tree_cache = tree_cache
        self.tree_operations = tree_operations
        self.config = config
        self.event_bus = event_bus
        self.logger = logger
        self.action_service = action_service

    def getEventType(self) -> type[RoomSpaceChildEvent]:
        return RoomSpaceChildEvent

    async def onEvent(self, room: MatrixRoom, event: RoomSpaceChildEvent):
        parent_id = room.room_id
        new_room_id = event.state_key
        self.logger.debug("New RoomSpaceChildEvent.")
        if (watched_space := self.config.watched_space) not in self.tree_cache:
            self.logger.info("Updating room tree.")
            tree = (await self.tree_operations
                              .fetch_tree_and_join_on_all_public_nodes(watched_space))
            tree.childs_which_need_user_promotion.append(new_room_id)
            self.tree_cache[watched_space] = tree
            await self.event_bus.publish(TreeStructureUpdated(tree))
        else:
            tree = self.tree_cache[watched_space]
            known_rooms = tree.child_ids
            if new_room_id not in known_rooms and parent_id in known_rooms:
                self.logger.info("Updating room tree.")
                self.logger.info(f"New room {new_room_id} in watched space.")
                self.logger.debug("Known rooms in cache.", extra={'childs':known_rooms})
                subtree = (await self.tree_operations
                              .fetch_tree_and_join_on_all_public_nodes(new_room_id))
                tree.add_node_to_tree(parent_id, subtree.root)
                tree.childs_which_need_user_promotion.extend(subtree.child_ids)
                await self.event_bus.publish(TreeStructureUpdated(tree))

@singleton
class RespondOnTreeRequest(ListenerInterface[UnknownEvent]):
    @inject
    def __init__(
        self,
        tree_builder: MatrixTreeBuilder,
        tree_operations: MatrixTreeOperations,
        config: Configuration,
        logger: MatrixLogger
    ):
        self.config = config
        self.tree_builder = tree_builder
        self.tree_operations = tree_operations
        self.logger = logger

    def getEventType(self) -> type[UnknownEvent]:
        return UnknownEvent

    async def onEvent(self, room: MatrixRoom, event: UnknownEvent):
        if event.type == 'org.herald.tree_structure_request':
            self.logger.info(f"Room tree requested by widget in room {room.room_id}.")
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
