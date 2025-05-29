from __future__ import annotations

from attrs import frozen
from dataclasses import dataclass
from datetime import date
from enum import Enum

from domain.dropped_fraction import DroppedFraction


class VisitorType(Enum):
    PRIVATE = "private"
    BUSINESS = "business"

    @staticmethod
    def from_string(type: str) -> VisitorType:
        if type == "private":
            return VisitorType.PRIVATE
        if type == "business":
            return VisitorType.BUSINESS

        raise ValueError(f"incorrect visitor type: {type}")


@frozen
class Visitor:
    unit_id: str
    city: str
    type: VisitorType
    email: str


@dataclass(frozen=True)
class Visit:
    date: date
    visitor: Visitor
    dropped_fractions: list[DroppedFraction]

    def __post_init__(self):
        if not isinstance(self.visitor, Visitor):
            raise ValueError("invalid visitor")

    def in_same_month(self, other: Visit) -> bool:
        return (
            self.visitor == other.visitor
            and self.date.year == other.date.year
            and self.date.month == other.date.month
        )
