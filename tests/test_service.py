import asyncio
from decimal import Decimal

import pytest

from mtgprices.errors import DuplicateCardError, FetchError, InvalidLinkError, ParseError
from mtgprices.models import LinkInput, ParsedCard, Site
from mtgprices.service import CardService
from tests.conftest import GF_URL, SCG_URL


def test_add_card(repo, fetcher):
    service = CardService(repo, fetcher)
    card = asyncio.run(service.add_card(LinkInput(2, SCG_URL)))
    assert (card.site, card.quantity, card.name) == (Site.STARCITYGAMES, 2, "Prophetic Prism (Foil)")
    assert repo.list_cards() == [card]


def test_duplicate_does_not_fetch(repo, fetcher):
    service = CardService(repo, fetcher)
    asyncio.run(service.add_card(LinkInput(1, GF_URL)))
    with pytest.raises(DuplicateCardError):
        asyncio.run(service.add_card(LinkInput(1, GF_URL)))
    assert fetcher.requested == [GF_URL]


def test_invalid_input_does_not_fetch(repo, fetcher):
    service = CardService(repo, fetcher)
    with pytest.raises(InvalidLinkError):
        asyncio.run(service.add_card(LinkInput(1, "http://127.0.0.1/")))
    with pytest.raises(InvalidLinkError):
        asyncio.run(service.add_card(LinkInput(0, GF_URL)))
    assert fetcher.requested == []


def test_refresh_updates_price(repo, fetcher):
    card = repo.add(Site.GOLDFISH, GF_URL, 1, ParsedCard("Old name", "Old set", Decimal("1")))
    refreshed = asyncio.run(CardService(repo, fetcher).refresh_card(card.id))
    assert refreshed.price_usd == Decimal("6.96")
    assert refreshed.name == "Loran of the Third Path (Foil)"


def test_refresh_failure_is_stored(repo, fetcher):
    card = repo.add(Site.GOLDFISH, GF_URL, 1, ParsedCard("Loran", "BRO", Decimal("1")))
    fetcher.failing.add(GF_URL)
    with pytest.raises(FetchError):
        asyncio.run(CardService(repo, fetcher).refresh_card(card.id))
    stored = repo.get(card.id)
    assert stored.price_usd == Decimal("1")
    assert "404" in stored.last_error


def test_parse_error_on_changed_markup(repo, fetcher):
    fetcher.pages["mtggoldfish.com"] = "<html>Cloudflare</html>"
    with pytest.raises(ParseError):
        asyncio.run(CardService(repo, fetcher).add_card(LinkInput(1, GF_URL)))
    assert repo.list_cards() == []
