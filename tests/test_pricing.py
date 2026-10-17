from decimal import Decimal

import pytest

from mtgprices.pricing import format_amount, parse_rate, ruble_price


def test_ruble_price_rounds_dollars_up():
    assert ruble_price(Decimal("0.64"), Decimal("60")) == 60
    assert ruble_price(Decimal("75.94"), Decimal("60")) == 4560
    assert ruble_price(Decimal("2.00"), Decimal("92.5")) == Decimal("185.0")


@pytest.mark.parametrize(("raw", "expected"), [("60", "60.00"), ("92,5", "92.50"), (" 100.123 ", "100.12")])
def test_parse_rate(raw, expected):
    assert parse_rate(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["", "abc", "0", "-5", "NaN", "Infinity", "1e9"])
def test_parse_rate_rejects(raw):
    with pytest.raises(ValueError):
        parse_rate(raw)


def test_format_amount():
    assert format_amount(Decimal("60.00")) == "60"
    assert format_amount(Decimal("6.5")) == "6.50"
