import os
import requests, json
from dataclasses import dataclass
from datetime import date
from typing import Any

from attrs import define, field
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.external_users import ExternalUsers
from domain.visit_history import VisitHistories
from domain.visits import Visit, Visitor, VisitorType
from domain.weight import Weight
from messaging.message_bus import MessageBus


@dataclass(frozen=True)
class Response:
    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


@define
class PriceCalculator:
    _external_users: ExternalUsers = field(kw_only=True)
    _visit_histories: VisitHistories = field(kw_only=True)
    _message_bus: MessageBus = field(kw_only=True)

    def calculate(self, visit_params: dict[str, Any]) -> Response:
        user = self._external_users.get_user_by_id(visit_params["person_id"])
        visitor = Visitor(
            unit_id=f"{user.city}-{user.address}",
            city=user.city,
            type=VisitorType.from_string(user.type),
            email=user.email,
        )
        dropped_fractions = [
            self.__parse_dropped_fraction(dropped_fraction)
            for dropped_fraction in visit_params["dropped_fractions"]
        ]

        visit = Visit(
            date.fromisoformat(visit_params["date"]),
            visitor,
            dropped_fractions,
        )
        history = self._visit_histories.find_by_visitor(visitor)
        history.visit(visit)
        calculated_price_of_visit = history.calculate_price_of_last_visit()

        self._visit_histories.save(history)
        self._message_bus.publish(calculated_price_of_visit)

        return Response(
            price_amount=round(calculated_price_of_visit.price.amount, 2),
            price_currency=str(calculated_price_of_visit.price.currency),
            person_id=visit_params["person_id"],
            visit_id=visit_params["visit_id"],
        )

    def __parse_dropped_fraction(self, dropped_fraction: Any) -> DroppedFraction:
        return DroppedFraction(
            FractionType.from_string(dropped_fraction["fraction_type"]),
            Weight(dropped_fraction["amount_dropped"]),
        )
