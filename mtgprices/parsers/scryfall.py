import json
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from mtgprices.errors import ParseError
from mtgprices.models import ParsedCard, Site
from mtgprices.parsers.base import Parser

API_HOST = "api.scryfall.com"


class ScryfallParser(Parser):
    """Scryfall отдаёт цены через JSON API, поэтому HTML страницы карты не нужен.

    Ссылка на страницу https://scryfall.com/card/bro/12/loran-of-the-third-path
    превращается в https://api.scryfall.com/cards/bro/12. Вариант карты выбирается
    фрагментом ссылки: #foil или #etched (по умолчанию обычная).
    """

    site = Site.SCRYFALL

    def source_url(self, url: str) -> str:
        parts = urlsplit(url)
        if parts.hostname == API_HOST:
            return url
        segments = [segment for segment in parts.path.split("/") if segment]
        if len(segments) < 3 or segments[0] != "card":
            raise ParseError(f"Ожидается ссылка вида https://scryfall.com/card/<сет>/<номер>/...: {url}")
        return f"https://{API_HOST}/cards/{segments[1]}/{segments[2]}"

    def parse(self, text: str, url: str) -> ParsedCard:
        try:
            data = json.loads(text)
            prices = data["prices"]
            name, set_name = data["name"], data["set_name"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ParseError(f"Не удалось разобрать ответ Scryfall: {url}") from exc

        finish = urlsplit(url).fragment.lower()
        if finish in ("foil", "etched"):
            usd = prices.get(f"usd_{finish}")
            name += f" ({finish.capitalize()})"
        else:
            # Карты, которые печатались только фойлом, не имеют обычной цены
            usd = prices.get("usd") or prices.get("usd_foil")
        if usd is None:
            raise ParseError(f"Scryfall не знает цену в долларах для этого варианта: {url}")
        return ParsedCard(
            name=name, set_name=set_name, price_usd=_decimal(usd, url), price_tix=_optional(prices.get("tix"))
        )


def _decimal(value: str, url: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ParseError(f"Некорректная цена Scryfall {value!r}: {url}") from exc


def _optional(value: str | None) -> Decimal | None:
    try:
        return Decimal(value) if value is not None else None
    except InvalidOperation:
        return None
