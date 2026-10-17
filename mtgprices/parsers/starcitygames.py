import re
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

from mtgprices.models import ParsedCard, Site
from mtgprices.parsers.base import HtmlParser, clean_text, parse_price

# SKU вида SGL-MTG-CMR-334-ENF1: «F» перед номером варианта означает фойл,
# в адресе страницы тот же признак стоит в конце: ...-334-enf/
_FOIL_SKU_RE = re.compile(r"F\d*$")
_FOIL_SLUG_RE = re.compile(r"-[a-z]{2}f/?$", re.IGNORECASE)


class StarCityGamesParser(HtmlParser):
    site = Site.STARCITYGAMES

    def _parse(self, soup: BeautifulSoup, url: str) -> ParsedCard:
        name = clean_text(self._require(soup.select_one("h1.productView-title"), "название", url).get_text())
        if _is_foil(url):
            name += " (Foil)"

        # <title>Prophetic Prism | Commander Legends | Star City Games</title>
        title = clean_text(self._require(soup.find("title"), "заголовок", url).get_text())
        parts = [part.strip() for part in title.split("|")]
        set_name = parts[1] if len(parts) >= 3 else ""

        price_el = soup.select_one(".productView-price .price--withoutTax") or soup.select_one(".price--withoutTax")
        if price_el is not None:
            price = parse_price(price_el.get_text())
        else:
            meta = self._require(soup.find("meta", attrs={"property": "product:price:amount"}), "цена", url)
            price = parse_price(str(meta.get("content") or ""))
        return ParsedCard(name=name, set_name=set_name, price_usd=price)


def _is_foil(url: str) -> bool:
    parts = urlsplit(url)
    sku = parse_qs(parts.query).get("sku")
    if sku:
        return bool(_FOIL_SKU_RE.search(sku[0]))
    return bool(_FOIL_SLUG_RE.search(parts.path))
