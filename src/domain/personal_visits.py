import abc
from functools import reduce

import attr
from attrs import define, field

from domain.dropped_fraction import DroppedFraction
from domain.price import Currency, Price
from domain.prices import PriceCalculator
from domain.visits import Visit, Visitor, VisitorType


@define
class PersonalVisitHistory:
    _visits: list[Visit] = field(default=attr.Factory(list))
    visitor: Visitor = field(kw_only=True)
    _calculators: list[PriceCalculator] = field(kw_only=True)

    def visit(self, visit: Visit) -> None:
        self._visits.append(visit)

    def calculate_price_of_last_visit(self) -> Price:
        last_visit = self.last_visit()

        price = reduce(
            lambda price, dropped_fraction: price.add(
                self._calculate(dropped_fraction)
            ),
            last_visit.dropped_fractions,
            Price(0, Currency.EUR),
        )

        if (
            self.visitor.type == VisitorType.PRIVATE
            and self.visits_in_current_month() >= 3
        ):
            price = price.times(1.05)

        return price

    def last_visit(self) -> Visit:
        return self._visits[-1]

    def visits_in_current_month(self) -> int:
        last_visit = self.last_visit()
        visits = sum(1 for visit in self._visits if visit.in_same_month(last_visit))
        return visits

    def _calculate(self, dropped_fraction: DroppedFraction):
        return reduce(
            lambda price, calculator: price.add(calculator.calculate(dropped_fraction)),
            self._calculators,
            Price(0, Currency.EUR),
        )


class PersonalVisitHistories(abc.ABC):
    @abc.abstractmethod
    def find_by_visitor(self, visitor: Visitor) -> PersonalVisitHistory:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, history: PersonalVisitHistory) -> None:
        raise NotImplementedError
