import abc
from domain.events.event import Event
from messaging.subscriber import Subscriber


class MessageBus(abc.ABC):
    @abc.abstractmethod
    def publish(self, ev: Event) -> None:
        pass

    @abc.abstractmethod
    def subscribe(self, sub: Subscriber) -> None:
        pass