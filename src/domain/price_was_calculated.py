from domain.price import Price
from dataclasses import dataclass

@dataclass(frozen=True)
class PriceWasCalculated:
    price: Price
    visitor_id: str
