import attr
from attrs import define, field
from domain.dropped_fraction import FractionType
from domain.visit_history import VisitHistories, VisitHistory
from domain.prices import PriceCatalog
from domain.visits import Visitor


@define
class InMemoryVisitHistories(VisitHistories):
    _histories: list[VisitHistory] = field(default=attr.Factory(list))
    _prices: PriceCatalog = field(kw_only=True)

    def find_by_visitor(self, visitor: Visitor) -> VisitHistory:
        history = next(
            (history for history in self._histories if history.visitor == visitor),
            None,
        )
        if history:
            return history
        else:
            history = VisitHistory(
                visitor=visitor, calculators=self._calculators(visitor)
            )
            self._histories.append(history)
            return history

    def save(self, history: VisitHistory) -> None:
        self._histories = [
            history if h.visitor == history.visitor else h for h in self._histories
        ]

    def _calculators(self, visitor: Visitor):
        return [
            self._prices.find(fraction_type, visitor)
            for fraction_type in list(FractionType)
        ]
