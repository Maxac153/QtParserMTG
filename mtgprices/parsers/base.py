import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup, Tag

from mtgprices.errors import ParseError
from mtgprices.models import ParsedCard, Site

_PRICE_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")


class Parser(ABC):
    site: Site

    def source_url(self, url: str) -> str:
        """Адрес, который нужно скачать для карты по ссылке url."""
        return url

    @abstractmethod
    def parse(self, text: str, url: str) -> ParsedCard: ...


class HtmlParser(Parser):
    def parse(self, text: str, url: str) -> ParsedCard:
        soup = BeautifulSoup(text, "html.parser")
        try:
            return self._parse(soup, url)
        except ParseError:
            raise
        except (AttributeError, IndexError, ValueError) as exc:
            raise ParseError(f"Не удалось разобрать страницу {self.site.label}: {url}") from exc

    @abstractmethod
    def _parse(self, soup: BeautifulSoup, url: str) -> ParsedCard: ...

    def _require(self, element: Tag | None, what: str, url: str) -> Tag:
        if element is None:
            raise ParseError(f"На странице {self.site.label} не найдено: {what} ({url})")
        return element


def clean_text(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def parse_price(text: str) -> Decimal:
    match = _PRICE_RE.search(text)
    if match is None:
        raise ParseError(f"Не удалось распознать цену: {clean_text(text)!r}")
    try:
        return Decimal(match.group().replace(",", ""))
    except InvalidOperation as exc:
        raise ParseError(f"Не удалось распознать цену: {clean_text(text)!r}") from exc
