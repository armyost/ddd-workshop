from domain.visits import Visits, Visit


class InMemoryVisits(Visits):
    _visits: list[Visit]

    def __init__(self):
        self._visits = []

    def visit(self, visit: Visit) -> None:
        self._visits.append(visit)

    def visits_in_current_month(self) -> int:
        last_visit = self.last_visit()
        visits = sum(1 for visit in self._visits if visit.in_same_month(last_visit))
        return visits

    def last_visit(self) -> Visit:
        return self._visits[-1]
