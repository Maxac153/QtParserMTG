import asyncio
from decimal import Decimal

import httpx
import pytest

from mtgprices.errors import FetchError
from mtgprices.rates import CBR_DAILY_URL, fetch_cbr_usd_rate, parse_cbr_usd
from tests.conftest import FIXTURES


def test_parse_saved_cbr_response():
    assert parse_cbr_usd((FIXTURES / "cbr_daily.xml").read_bytes()) == Decimal("83.62")


def test_parse_uses_nominal():
    xml = "<ValCurs><Valute><CharCode>USD</CharCode><Nominal>10</Nominal><Value>900,5</Value></Valute></ValCurs>"
    assert parse_cbr_usd(xml.encode()) == Decimal("90.05")


@pytest.mark.parametrize(
    "xml",
    [
        b"<ValCurs></ValCurs>",
        b"not xml",
        b"<ValCurs><Valute><CharCode>USD</CharCode><Value>x</Value></Valute></ValCurs>",
    ],
)
def test_parse_errors(xml):
    with pytest.raises(FetchError):
        parse_cbr_usd(xml)


def test_fetch():
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(200, content=(FIXTURES / "cbr_daily.xml").read_bytes())

    assert asyncio.run(fetch_cbr_usd_rate(httpx.MockTransport(handler))) == Decimal("83.62")
    assert seen == [CBR_DAILY_URL]


def test_fetch_http_error():
    with pytest.raises(FetchError):
        asyncio.run(fetch_cbr_usd_rate(httpx.MockTransport(lambda request: httpx.Response(500))))
