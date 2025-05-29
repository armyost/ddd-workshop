from typing import Iterator

from domain.events.event import Event
from messaging.message_bus import MessageBus
from messaging.subscriber import Subscriber


class InMemoryMessageBus(MessageBus):
    _subscribers: list[Subscriber] = []

    def __init__(self):
        self._subscribers = []

    def publish(self, ev: Event) -> None:
        for subscriber in self._subscribers: subscriber(ev)

    def subscribe(self, sub: Subscriber) -> None:
        self._subscribers.append(sub)
