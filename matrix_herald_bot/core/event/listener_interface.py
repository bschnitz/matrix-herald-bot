class CoreListenerInterface[T]:
    """Each listener must define the event type it handles and how to handle it."""

    def getEventType(self) -> type[T]:
        raise NotImplementedError

    async def onEvent(self, event: T):
        raise NotImplementedError
