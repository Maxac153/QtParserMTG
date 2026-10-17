import asyncio
from typing import Any, Protocol

from mtgprices.errors import DuplicateCardError, MtgPricesError
from mtgprices.links import check_quantity, validate_link
from mtgprices.models import Card, LinkInput, ParsedCard
from mtgprices.parsers import get_parser
from mtgprices.repository import CardRepository


class PageFetcher(Protocol):
    async def fetch(self, url: str) -> str: ...


class CardService:
    """Сценарии работы с картами. Источник истины — база данных, а не интерфейс."""

    def __init__(self, repo: CardRepository, fetcher: PageFetcher):
        self.repo = repo
        self.fetcher = fetcher

    async def fetch_card(self, url: str) -> ParsedCard:
        parser = get_parser(validate_link(url))
        text = await self.fetcher.fetch(parser.source_url(url))
        # BeautifulSoup работает синхронно, не блокируем цикл событий
        return await asyncio.to_thread(parser.parse, text, url)

    async def add_card(self, item: LinkInput) -> Card:
        site = validate_link(item.url)
        check_quantity(item.quantity)
        # Проверяем до запроса, чтобы не скачивать страницу зря
        if self.repo.exists(site, item.url):
            raise DuplicateCardError(f"Карта уже есть в списке: {item.url}")
        parsed = await self.fetch_card(item.url)
        return self.repo.add(site, item.url, item.quantity, parsed)

    async def refresh_card(self, card_id: int) -> Card:
        card = self.repo.get(card_id)
        try:
            parsed = await self.fetch_card(card.url)
        except MtgPricesError as exc:
            self.repo.set_error(card_id, str(exc))
            raise
        return self.repo.update_from_parsed(card_id, parsed)

    # Обработчики элементов фоновых задач: payload приходит из БД в виде JSON

    async def add_card_job_item(self, payload: dict[str, Any]) -> None:
        await self.add_card(LinkInput(int(payload["quantity"]), str(payload["url"])))

    async def refresh_card_job_item(self, payload: int) -> None:
        await self.refresh_card(int(payload))
