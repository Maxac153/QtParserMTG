"""Официальный курс доллара ЦБ РФ."""

import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation

import httpx

from mtgprices.errors import FetchError

CBR_DAILY_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def parse_cbr_usd(xml: bytes) -> Decimal:
    """Курс из XML_daily.asp: <Valute><CharCode>USD</CharCode><Nominal>1</Nominal><Value>83,6177</Value>."""
    try:
        root = ET.fromstring(xml)
        for valute in root.iter("Valute"):
            if valute.findtext("CharCode") == "USD":
                value = Decimal((valute.findtext("Value") or "").replace(",", "."))
                nominal = Decimal(valute.findtext("Nominal") or "1")
                return (value / nominal).quantize(Decimal("0.01"))
    except (ET.ParseError, InvalidOperation) as exc:
        raise FetchError("Не удалось разобрать ответ ЦБ РФ") from exc
    raise FetchError("В ответе ЦБ РФ нет курса доллара")


async def fetch_cbr_usd_rate(transport: httpx.AsyncBaseTransport | None = None, timeout: float = 20.0) -> Decimal:
    try:
        async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
            response = await client.get(CBR_DAILY_URL)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise FetchError(f"Не удалось получить курс ЦБ РФ ({type(exc).__name__})") from exc
    return parse_cbr_usd(response.content)
