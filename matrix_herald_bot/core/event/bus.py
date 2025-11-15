import asyncio
from typing import Any
from injector import inject, singleton

from matrix_herald_bot.core.event.listener_interface import CoreListenerInterface

@singleton
class EventBus:
    @inject
    def __init__(self, listeners: list[CoreListenerInterface]):
        self.listeners = listeners

    async def publish(self, event: Any):
        for listener in self.listeners:
            if isinstance(event, listener.getEventType()):
                result = listener.onEvent(event)
                if asyncio.iscoroutine(result):
                    await result
