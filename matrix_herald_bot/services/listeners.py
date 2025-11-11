import json
from injector import Module, multiprovider
from nio import Event, MatrixRoom, UnknownEvent

class ListenerInterface[T: Event]:
    def getEventType(self) -> type[T]:
        raise NotImplementedError

    async def onEvent(self, room: MatrixRoom, event: T):
        raise NotImplementedError

class OnTreeRequest(ListenerInterface[UnknownEvent]):
    def getEventType(self) -> type[UnknownEvent]:
        return UnknownEvent

    async def onEvent(self, room: MatrixRoom, event: UnknownEvent):
        if event.type == 'org.herald.tree_structure_request':
            print(f"OnTreeRequest")
            print(json.dumps(event.source, indent=4))

class OnOtherRequest(ListenerInterface[UnknownEvent]):
    def getEventType(self) -> type[UnknownEvent]:
        return UnknownEvent

    async def onEvent(self, room: MatrixRoom, event: UnknownEvent):
        print("onOtherRequest")

class ListenerCollectionModule(Module):
    @multiprovider
    def provide_my_collection_services(self) -> list[ListenerInterface]:
        return [OnTreeRequest(), OnOtherRequest()]
