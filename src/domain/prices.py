from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import cast

from attrs import define, field

from domain.dropped_fraction import DroppedFraction, FractionType
from domain.price import Currency, Price
from domain.visits import Visitor, VisitorType
from domain.weight import Weight


@dataclass(frozen=True)
class FixedPricePolicy:
    price: Price
    fraction_type: FractionType


@dataclass(frozen=True)
class ExcemptionPricePolicy:
    fraction_type: FractionType
    tiers: dict[Weight, Price]

    def __post_init__(self):
        previous = None

        for weight in self.tiers:
            if not previous:
                if weight != Weight(0):
                    raise ValueError("first tier has to be 0")
            else:
                if weight <= previous:
                    raise ValueError(f"invalid weight tier {weight}")
            previous = weight


class PriceCalculator:
    _fraction_type: FractionType
    _tiers: dict[Weight, Price]
    _current_weight_dropped: int

    def __init__(self, policy: ExcemptionPricePolicy):
        self._fraction_type = policy.fraction_type
        self._tiers = policy.tiers
        self._current_weight_dropped = 0

    def calculate(self, dropped_fraction: DroppedFraction) -> Price:
        if dropped_fraction.fraction_type != self._fraction_type:
            return Price(0, Currency.EUR)

        price = reduce(
            lambda total, weight_amount: total.add(
                self._tiers[weight_amount[0]].times(weight_amount[1])
            ),
            self._calculate_price_tiers(dropped_fraction.weight.weight),
            Price(0, Currency.EUR),
        )
        self._current_weight_dropped = (
            self._current_weight_dropped + dropped_fraction.weight.weight
        )

        return price

    def _calculate_price_tiers(self, weight_dropped: float):
        current_dropped_weight_remaining = self._current_weight_dropped
        weight_remaining = weight_dropped

        tiers: list[tuple[Weight, float]] = []

        previous_weight = None
        for weight in self._tiers:
            if previous_weight:
                weight_in_tier = weight.weight - previous_weight.weight
                weight_in_tier_remaining = max(
                    0, weight_in_tier - current_dropped_weight_remaining
                )
                weight_to_add = min(weight_remaining, weight_in_tier_remaining)

                if weight_to_add > 0:
                    tiers.append((previous_weight, weight_to_add))

                weight_remaining = weight_remaining - weight_to_add
                current_dropped_weight_remaining = (
                    current_dropped_weight_remaining - weight_in_tier
                )
            previous_weight = weight

        if weight_remaining > 0:
            tiers.append((weight, weight_remaining))

        return tiers


@dataclass(frozen=True)
class PriceKey:
    fraction_type: FractionType
    visitor_type: VisitorType
    city: str


@define
class PriceCatalog:
    _calculators: dict[PriceKey, ExcemptionPricePolicy] = field(init=False, default={})

    def add(
        self, key: PriceKey, policy: FixedPricePolicy | ExcemptionPricePolicy
    ) -> PriceCatalog:
        p = cast(
            ExcemptionPricePolicy,
            ExcemptionPricePolicy(policy.fraction_type, {Weight(0): policy.price})
            if isinstance(policy, FixedPricePolicy)
            else policy,
        )

        self._calculators[key] = p

        return self

    def find(self, fraction_type: FractionType, visitor: Visitor) -> PriceCalculator:
        key = PriceKey(fraction_type, visitor.type, visitor.city)
        policy = self._calculators[key]
        return PriceCalculator(policy)
