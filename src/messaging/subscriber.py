import abc
from domain.events.event import Event

class Subscriber(abc.ABC):
    @abc.abstractmethod
    def publish(self, ev: Event) -> None :
        pass