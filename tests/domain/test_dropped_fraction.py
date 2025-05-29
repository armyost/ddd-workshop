import pytest
from domain.dropped_fraction import FractionType


def test_parse_fraction_type() -> None:
    assert FractionType.from_string("Green waste")


def test_incorrect_fraction_type() -> None:
    with pytest.raises(ValueError):
        FractionType.from_string("incorrect")
