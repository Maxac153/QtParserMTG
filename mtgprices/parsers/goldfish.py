from bs4 import BeautifulSoup

from mtgprices.models import ParsedCard, Site
from mtgprices.parsers.base import HtmlParser, clean_text, parse_price


class GoldFishParser(HtmlParser):
    site = Site.GOLDFISH

    def _parse(self, soup: BeautifulSoup, url: str) -> ParsedCard:
        header = self._require(soup.select_one(".price-card-name-header-name"), "название", url)
        name_el = header.select_one(".card_name") or header
        # <span class='card_name'>Loran of the Third Path <span class='card-num'>#12</span>
        #   <span class='badge'>Foil</span></span>
        name = clean_text("".join(name_el.find_all(string=True, recursive=False)))
        badges = [clean_text(badge.get_text()) for badge in name_el.select(".badge")]
        if badges:
            name += f" ({', '.join(badges)})"

        set_el = soup.select_one(".price-card-name-header-set .price-card-name-set-name") or soup.select_one(
            "span.price-card-name-set-name"
        )
        set_name = clean_text(self._require(set_el, "сет", url).get_text())

        # Основная цена — бумажная в долларах; цена MTGO указана в tix и хранится отдельно
        price_el = soup.select_one(".price-box.paper .price-box-price")
        price = parse_price(self._require(price_el, "цена", url).get_text())
        tix_el = soup.select_one(".price-box.online .price-box-price")
        tix = parse_price(tix_el.get_text()) if tix_el is not None else None
        return ParsedCard(name=name, set_name=set_name, price_usd=price, price_tix=tix)
