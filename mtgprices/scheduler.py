"""Автоматическое обновление цен и курса, пока запущен сервер.

Время последнего запуска хранится в БД, поэтому перезапуск сервера не сбивает расписание.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from mtgprices.errors import MtgPricesError
from mtgprices.repository import CardRepository, now_iso

log = logging.getLogger(__name__)

RATE_UPDATE_INTERVAL = timedelta(hours=12)
MAX_REFRESH_HOURS = 24 * 30

KEY_REFRESH_HOURS = "auto_refresh_hours"
KEY_LAST_REFRESH = "last_auto_refresh"
KEY_AUTO_RATE = "auto_rate"
KEY_LAST_RATE = "last_rate_update"


@dataclass(frozen=True)
class AutoSettings:
    refresh_hours: int
    auto_rate: bool
    last_refresh: str | None
    last_rate_update: str | None


def load_auto_settings(repo: CardRepository) -> AutoSettings:
    return AutoSettings(
        refresh_hours=int(repo.get_setting(KEY_REFRESH_HOURS) or 0),
        auto_rate=repo.get_setting(KEY_AUTO_RATE) == "1",
        last_refresh=repo.get_setting(KEY_LAST_REFRESH),
        last_rate_update=repo.get_setting(KEY_LAST_RATE),
    )


def save_auto_settings(repo: CardRepository, refresh_hours: int, auto_rate: bool) -> None:
    if not 0 <= refresh_hours <= MAX_REFRESH_HOURS:
        raise ValueError(f"Интервал обновления должен быть от 0 до {MAX_REFRESH_HOURS} часов")
    repo.set_setting(KEY_REFRESH_HOURS, str(refresh_hours))
    repo.set_setting(KEY_AUTO_RATE, "1" if auto_rate else "0")


def _due(last: str | None, interval: timedelta, now: datetime) -> bool:
    return last is None or datetime.fromisoformat(last) + interval <= now


class Scheduler:
    def __init__(
        self,
        repo: CardRepository,
        start_refresh: Callable[[], str | None],
        fetch_rate: Callable[[], Awaitable[Decimal]],
        check_every: float = 60.0,
    ):
        self.repo = repo
        self.start_refresh = start_refresh
        self.fetch_rate = fetch_rate
        self.check_every = check_every

    async def run(self) -> None:
        while True:
            try:
                await self.tick()
            except Exception:
                log.exception("Ошибка планировщика")
            await asyncio.sleep(self.check_every)

    async def tick(self, now: datetime | None = None) -> None:
        now = now or datetime.now(UTC)
        settings = load_auto_settings(self.repo)

        if settings.auto_rate and _due(settings.last_rate_update, RATE_UPDATE_INTERVAL, now):
            await self.update_rate()

        if settings.refresh_hours > 0 and _due(settings.last_refresh, timedelta(hours=settings.refresh_hours), now):
            # Отметку ставим и когда обновлять нечего, чтобы не проверять каждую минуту
            self.start_refresh()
            self.repo.set_setting(KEY_LAST_REFRESH, now.isoformat(timespec="seconds"))

    async def update_rate(self) -> Decimal | None:
        try:
            rate = await self.fetch_rate()
        except MtgPricesError as exc:
            log.warning("Курс ЦБ не обновлён: %s", exc)
            return None
        finally:
            self.repo.set_setting(KEY_LAST_RATE, now_iso())
        self.repo.set_rate(rate)
        return rate
