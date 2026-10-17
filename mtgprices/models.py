from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class Site(StrEnum):
    STARCITYGAMES = "starcitygames"
    GOLDFISH = "goldfish"
    SCRYFALL = "scryfall"

    @property
    def label(self) -> str:
        return _SITE_LABELS[self]


_SITE_LABELS = {
    Site.STARCITYGAMES: "StarCityGames",
    Site.GOLDFISH: "MTGGoldfish",
    Site.SCRYFALL: "Scryfall",
}


@dataclass(frozen=True)
class ParsedCard:
    """Данные, извлечённые со страницы карты."""

    name: str
    set_name: str
    price_usd: Decimal
    # Цена MTGO в tix, если сайт её показывает
    price_tix: Decimal | None = None


@dataclass(frozen=True)
class Card:
    id: int
    site: Site
    url: str
    quantity: int
    name: str
    set_name: str
    price_usd: Decimal | None
    updated_at: str | None
    last_error: str | None = None
    price_tix: Decimal | None = None
    # Цена из предыдущей записи истории, чтобы показать изменение
    previous_price_usd: Decimal | None = None


@dataclass(frozen=True)
class PricePoint:
    checked_at: str | None
    price_usd: Decimal | None
    price_tix: Decimal | None


@dataclass(frozen=True)
class LinkInput:
    """Строка ввода пользователя: сколько карт и по какой ссылке."""

    quantity: int
    url: str
