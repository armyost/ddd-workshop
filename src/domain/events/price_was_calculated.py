from domain.price import Price
from dataclasses import dataclass
from domain.events.event import Event
from domain.visits import Visitor

@dataclass(frozen=True)
class PriceWasCalculated(Event):
    price: Price
    visitor: Visitor
