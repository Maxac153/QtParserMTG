"""Простой SVG-график цены, который рисуется на сервере (без JS-библиотек)."""

from dataclasses import dataclass
from decimal import Decimal

from mtgprices.models import PricePoint

WIDTH = 640
HEIGHT = 220
PADDING_X = 48
PADDING_Y = 20


@dataclass(frozen=True)
class Chart:
    width: int
    height: int
    points: str
    dots: list[tuple[float, float]]
    min_price: Decimal
    max_price: Decimal
    min_y: float
    max_y: float


def price_chart(history: list[PricePoint]) -> Chart | None:
    prices = [point.price_usd for point in history if point.price_usd is not None]
    if len(prices) < 2:
        return None
    low, high = min(prices), max(prices)
    span = high - low or Decimal(1)
    step = (WIDTH - 2 * PADDING_X) / (len(prices) - 1)

    def y(price: Decimal) -> float:
        return round(HEIGHT - PADDING_Y - float((price - low) / span) * (HEIGHT - 2 * PADDING_Y), 1)

    dots = [(round(PADDING_X + index * step, 1), y(price)) for index, price in enumerate(prices)]
    return Chart(
        width=WIDTH,
        height=HEIGHT,
        points=" ".join(f"{x},{y_}" for x, y_ in dots),
        dots=dots,
        min_price=low,
        max_price=high,
        min_y=y(low),
        max_y=y(high),
    )
