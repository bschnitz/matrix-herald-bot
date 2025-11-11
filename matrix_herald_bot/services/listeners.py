from injector import Injector, Module, inject, multiprovider
from nio import Event, MatrixRoom, UnknownEvent
from matrix_herald_bot.config.model import Configuration
from matrix_herald_bot.services.tree_operations import MatrixTreeOperations
from matrix_herald_bot.services.tree_builder import MatrixTreeBuilder

class ListenerInterface[T: Event]:
    def getEventType(self) -> type[T]:
        raise NotImplementedError

    async def onEvent(self, room: MatrixRoom, event: T):
        raise NotImplementedError

class OnTreeRequest(ListenerInterface[UnknownEvent]):
    @inject
    def __init__(
        self,
        tree_builder: MatrixTreeBuilder,
        tree_operations: MatrixTreeOperations,
        config: Configuration
    ):
        self.config = config
        self.tree_builder = tree_builder
        self.tree_operations = tree_operations

    def getEventType(self) -> type[UnknownEvent]:
        return UnknownEvent

    async def onEvent(self, room: MatrixRoom, event: UnknownEvent):
        if event.type == 'org.herald.tree_structure_request':
            print("Sending tree to widget.")
            root = await self.tree_builder.fetch_tree(self.config.watched_spaces[0])
            await self.tree_operations.send_tree_to_room(
                root,
                room.room_id,
                "org.herald.tree_structure",
                event.source['state_key']
            )

class ListenerCollectionModule(Module):
    @multiprovider
    def provide_my_collection_services(self, injector: Injector) -> list[ListenerInterface]:
        return [injector.get(OnTreeRequest)]
