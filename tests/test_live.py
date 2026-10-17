"""Проверка на настоящих сайтах: не изменилась ли вёрстка. Запуск: pytest -m network"""

import asyncio

import pytest

from mtgprices.fetcher import Fetcher
from mtgprices.links import validate_link
from mtgprices.parsers import get_parser
from mtgprices.rates import fetch_cbr_usd_rate
from tests.conftest import GF_URL, SCG_URL

pytestmark = pytest.mark.network


@pytest.mark.parametrize("url", [SCG_URL, GF_URL, "https://scryfall.com/card/bro/12/loran-of-the-third-path"])
def test_live_page_parses(url):
    parser = get_parser(validate_link(url))

    async def run():
        fetcher = Fetcher(timeout=30)
        try:
            return await fetcher.fetch(parser.source_url(url))
        finally:
            await fetcher.aclose()

    card = parser.parse(asyncio.run(run()), url)
    assert card.name
    assert card.set_name
    assert card.price_usd > 0


def test_live_cbr_rate():
    assert asyncio.run(fetch_cbr_usd_rate()) > 0
