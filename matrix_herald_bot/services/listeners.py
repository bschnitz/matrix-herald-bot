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
        # The via-fiel in content idicates if the room was added or removed from
        # its parent
        room_is_added = 'via' in event.source['content']
        space_child = event.state_key
        self.logger.debug("New RoomSpaceChildEvent.", extra={'event': event.source})
        if (watched_space := self.config.watched_space) not in self.tree_cache:
            await self._initializeRoomTree(watched_space)
        elif room_is_added:
            await self._onRoomAdded(watched_space, space_child, parent_id)
        else:
            await self._onRoomRemoved(watched_space, space_child, parent_id)

    async def _initializeRoomTree(self, watched_space: str):
        self.logger.info("Initializing room tree.")
        tree = (await self.tree_operations
                          .fetch_tree_and_join_on_all_public_nodes(watched_space))
        self.tree_cache[watched_space] = tree
        await self.event_bus.publish(TreeStructureUpdated(tree))

    async def _onRoomAdded(
        self,
        watched_space: str,
        new_room_id: str,
        parent_id: str
    ):
        tree = self.tree_cache[watched_space]
        known_rooms = tree.child_ids
        if parent_id in known_rooms:
            self.logger.info(
                f"Updating room tree: New room {new_room_id} in watched space."
            )
            self.logger.debug("Known rooms in cache.", extra={'childs':known_rooms})
            subtree = (await self.tree_operations
                          .fetch_tree_and_join_on_all_public_nodes(new_room_id))
            tree.add_node(parent_id, subtree.root)
            # if child exists already in another part of the tree, there is no
            # need to promote the users in it again
            if new_room_id not in known_rooms:
                tree.childs_which_need_user_promotion.extend(subtree.child_ids)
            await self.event_bus.publish(TreeStructureUpdated(tree))

    async def _onRoomRemoved(
        self,
        watched_space: str,
        removed_room_id: str,
        parent_id: str
    ):
        tree = self.tree_cache[watched_space]
        known_rooms = tree.child_ids
        if parent_id in known_rooms:
            self.logger.info(
                "Updating room tree."
                f"Room {removed_room_id} was removed from its parent {parent_id}."
            )
            tree.remove_node(parent_id, removed_room_id)

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
