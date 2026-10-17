from decimal import Decimal

import pytest

from mtgprices.errors import ParseError
from mtgprices.models import Site
from mtgprices.parsers import get_parser
from mtgprices.parsers.base import clean_text, parse_price
from tests.conftest import GF_URL, SCG_URL


def test_starcitygames_foil(scg_html):
    card = get_parser(Site.STARCITYGAMES).parse(scg_html, SCG_URL)
    assert card.name == "Prophetic Prism (Foil)"
    assert card.set_name == "Commander Legends"
    assert card.price_usd == Decimal("0.35")


@pytest.mark.parametrize(
    ("url", "foil"),
    [
        ("https://starcitygames.com/x-sgl-mtg-cmr-334-enn/?sku=SGL-MTG-CMR-334-ENN1", False),
        ("https://starcitygames.com/x-sgl-mtg-cmr-334-enf/", True),
        ("https://starcitygames.com/x-sgl-mtg-cmr-334-enn/", False),
    ],
)
def test_starcitygames_foil_detection(scg_html, url, foil):
    card = get_parser(Site.STARCITYGAMES).parse(scg_html, url)
    assert card.name.endswith("(Foil)") is foil


def test_starcitygames_price_falls_back_to_meta():
    html = """<html><head><title>Bolt | Alpha | Star City Games</title>
    <meta property="product:price:amount" content="12.50"></head>
    <body><h1 class="productView-title"> Lightning Bolt </h1></body></html>"""
    card = get_parser(Site.STARCITYGAMES).parse(html, "https://starcitygames.com/bolt-enn/")
    assert card == card.__class__("Lightning Bolt", "Alpha", Decimal("12.50"))


def test_goldfish_paper_price_and_apostrophe(gf_html):
    card = get_parser(Site.GOLDFISH).parse(gf_html, GF_URL)
    assert card.name == "Loran of the Third Path (Foil)"
    assert card.set_name == "The Brothers' War"  # раньше апостроф превращался в пробел
    assert card.price_usd == Decimal("6.96")  # бумажная цена, а не 1.15 tix


@pytest.mark.parametrize("site", list(Site))
def test_unknown_markup_raises_parse_error(site):
    with pytest.raises(ParseError):
        get_parser(site).parse("<html><body>Access denied</body></html>", "https://example")


@pytest.mark.parametrize(
    ("text", "expected"),
    [("$ 6.96", "6.96"), ("$0.35", "0.35"), ("$1,234.50", "1234.50"), ("\n 12 \n", "12")],
)
def test_parse_price(text, expected):
    assert parse_price(text) == Decimal(expected)


def test_parse_price_without_number():
    with pytest.raises(ParseError):
        parse_price("нет в наличии")


def test_clean_text():
    assert clean_text("\n  The\xa0Brothers'\xa0War \n") == "The Brothers' War"


def test_goldfish_tix_price(gf_html):
    assert get_parser(Site.GOLDFISH).parse(gf_html, GF_URL).price_tix == Decimal("1.15")


SCRYFALL_URL = "https://scryfall.com/card/bro/12/loran-of-the-third-path"


@pytest.mark.parametrize(
    ("url", "api"),
    [
        (SCRYFALL_URL, "https://api.scryfall.com/cards/bro/12"),
        (SCRYFALL_URL + "?utm_source=api#foil", "https://api.scryfall.com/cards/bro/12"),
        ("https://api.scryfall.com/cards/bro/12", "https://api.scryfall.com/cards/bro/12"),
    ],
)
def test_scryfall_source_url(url, api):
    assert get_parser(Site.SCRYFALL).source_url(url) == api


def test_scryfall_source_url_rejects_other_pages():
    with pytest.raises(ParseError):
        get_parser(Site.SCRYFALL).source_url("https://scryfall.com/sets/bro")


@pytest.mark.parametrize(
    ("fragment", "name", "price"),
    [("", "Loran of the Third Path", "4.84"), ("#foil", "Loran of the Third Path (Foil)", "6.33")],
)
def test_scryfall_prices(scryfall_json, fragment, name, price):
    card = get_parser(Site.SCRYFALL).parse(scryfall_json, SCRYFALL_URL + fragment)
    assert (card.name, card.set_name, card.price_usd, card.price_tix) == (
        name,
        "The Brothers' War",
        Decimal(price),
        Decimal("0.09"),
    )


def test_scryfall_missing_variant_price(scryfall_json):
    with pytest.raises(ParseError, match="не знает цену"):
        get_parser(Site.SCRYFALL).parse(scryfall_json, SCRYFALL_URL + "#etched")


def test_scryfall_foil_only_card():
    text = '{"name": "X", "set_name": "S", "prices": {"usd": null, "usd_foil": "2.50", "tix": null}}'
    card = get_parser(Site.SCRYFALL).parse(text, SCRYFALL_URL)
    assert (card.price_usd, card.price_tix) == (Decimal("2.50"), None)


@pytest.mark.parametrize("text", ["not json", "{}", '{"name": "X", "set_name": "S", "prices": {"usd": "abc"}}'])
def test_scryfall_bad_response(text):
    with pytest.raises(ParseError):
        get_parser(Site.SCRYFALL).parse(text, SCRYFALL_URL)
