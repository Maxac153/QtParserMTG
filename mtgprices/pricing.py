import math
from decimal import Decimal, InvalidOperation

MAX_RATE = Decimal(100_000)


def ruble_price(price_usd: Decimal, rate: Decimal) -> Decimal:
    """Цена в рублях: доллары округляются вверх до целого и умножаются на курс."""
    return Decimal(math.ceil(price_usd)) * rate


def parse_rate(raw: str) -> Decimal:
    try:
        rate = Decimal(raw.strip().replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError("Курс должен быть числом") from exc
    if not rate.is_finite() or not 0 < rate <= MAX_RATE:
        raise ValueError(f"Курс должен быть больше 0 и не больше {MAX_RATE}")
    return rate.quantize(Decimal("0.01"))


def format_amount(value: Decimal) -> str:
    """60.00 -> «60», 6.5 -> «6.50»."""
    text = f"{value:.2f}"
    return text[:-3] if text.endswith(".00") else text
