import pytest
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.price import Currency, Price
from domain.prices import PriceCalculator, ExcemptionPricePolicy
from domain.weight import Weight


def test_price_is_0():
    calculator = PriceCalculator(
        ExcemptionPricePolicy(
            FractionType.CONSTRUCTION_WASTE, tiers={Weight(0): Price(0, Currency.EUR)}
        )
    )

    assert Price(0, Currency.EUR) == calculator.calculate(
        DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(10))
    )


def test_fixed_price():
    calculator = PriceCalculator(
        ExcemptionPricePolicy(
            FractionType.CONSTRUCTION_WASTE, tiers={Weight(0): Price(0.2, Currency.EUR)}
        )
    )

    assert Price(2, Currency.EUR) == calculator.calculate(
        DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(10))
    )


def test_other_fraction_type():
    calculator = PriceCalculator(
        ExcemptionPricePolicy(
            FractionType.CONSTRUCTION_WASTE, tiers={Weight(0): Price(0.2, Currency.EUR)}
        )
    )

    assert Price(0, Currency.EUR) == calculator.calculate(
        DroppedFraction(FractionType.GREEN_WASTE, Weight(10))
    )


tier_data = [
    (Weight(9), Price(0.2 * 9, Currency.EUR)),
    (Weight(15), Price(0.2 * 10 + 5 * 0.5, Currency.EUR)),
    (Weight(23), Price(0.2 * 10 + 13 * 0.5, Currency.EUR)),
]


@pytest.mark.parametrize("weight, expected", tier_data)
def test_price_tiers(weight, expected):
    calculator = PriceCalculator(
        ExcemptionPricePolicy(
            FractionType.CONSTRUCTION_WASTE,
            tiers={
                Weight(0): Price(0.2, Currency.EUR),
                Weight(10): Price(0.5, Currency.EUR),
            },
        )
    )

    assert expected == calculator.calculate(
        DroppedFraction(FractionType.CONSTRUCTION_WASTE, weight)
    )


def test_price_tiers_accum():
    calculator = PriceCalculator(
        ExcemptionPricePolicy(
            FractionType.CONSTRUCTION_WASTE,
            tiers={
                Weight(0): Price(0.2, Currency.EUR),
                Weight(10): Price(0.5, Currency.EUR),
            },
        )
    )

    assert Price(0.2 * 9, Currency.EUR) == calculator.calculate(
        DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(9))
    )
    assert Price(0.2 * 1 + 0.5 * 14, Currency.EUR) == calculator.calculate(
        DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(15))
    )
    # assert Price(0.2 * 10 + 0.5 * 13, Currency.EUR) == calculator.calculate(
    #     DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(23))
    # )


# def test_build_excemption_price_policy():
#     fixed1 = FixedPricePolicy(
#         Price(0.23, Currency.EUR), FractionType.CONSTRUCTION_WASTE
#     )

#     assert ExcemptionPricePolicy(
#         {Weight(0): fixed1, Weight(20): fixed1, Weight(30): fixed1}
#     )


# def test_build_invalid_excemption_price_policy():
#     fixed1 = FixedPricePolicy(
#         Price(0.23, Currency.EUR), FractionType.CONSTRUCTION_WASTE
#     )
#     with pytest.raises(ValueError):
#         ExcemptionPricePolicy(
#             {Weight(0): fixed1, Weight(20): fixed1, Weight(15): fixed1}
#         )


# def test_excemption_must_start_with_0_weight_tier():
#     fixed1 = FixedPricePolicy(
#         Price(0.23, Currency.EUR), FractionType.CONSTRUCTION_WASTE
#     )
#     with pytest.raises(ValueError):
#         ExcemptionPricePolicy({Weight(10): fixed1})
