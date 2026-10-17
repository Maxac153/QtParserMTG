import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from mtgprices.errors import FetchError
from mtgprices.scheduler import KEY_LAST_REFRESH, Scheduler, load_auto_settings, save_auto_settings

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)


class Calls:
    def __init__(self, rate=Decimal("83.62")):
        self.refreshes = 0
        self.rate_requests = 0
        self.rate = rate

    def start_refresh(self):
        self.refreshes += 1
        return "job"

    async def fetch_rate(self):
        self.rate_requests += 1
        if isinstance(self.rate, Exception):
            raise self.rate
        return self.rate


def make(repo, calls):
    return Scheduler(repo, calls.start_refresh, calls.fetch_rate)


def test_disabled_by_default(repo):
    calls = Calls()
    asyncio.run(make(repo, calls).tick(NOW))
    assert (calls.refreshes, calls.rate_requests) == (0, 0)
    assert load_auto_settings(repo).refresh_hours == 0


def test_refresh_interval(repo):
    save_auto_settings(repo, refresh_hours=24, auto_rate=False)
    calls = Calls()
    scheduler = make(repo, calls)
    asyncio.run(scheduler.tick(NOW))
    assert calls.refreshes == 1
    asyncio.run(scheduler.tick(NOW + timedelta(hours=1)))
    assert calls.refreshes == 1
    # Время последнего запуска берётся из БД, поэтому тест сдвигает его вручную
    repo.set_setting(KEY_LAST_REFRESH, (NOW - timedelta(hours=25)).isoformat())
    asyncio.run(scheduler.tick(NOW))
    assert calls.refreshes == 2


def test_auto_rate(repo):
    save_auto_settings(repo, refresh_hours=0, auto_rate=True)
    calls = Calls()
    scheduler = make(repo, calls)
    asyncio.run(scheduler.tick(NOW))
    asyncio.run(scheduler.tick(NOW + timedelta(hours=1)))
    assert calls.rate_requests == 1
    assert repo.get_rate() == Decimal("83.62")


def test_failed_rate_keeps_old_value(repo):
    repo.set_rate(Decimal("90"))
    calls = Calls(rate=FetchError("нет сети"))
    assert asyncio.run(make(repo, calls).update_rate()) is None
    assert repo.get_rate() == Decimal("90")
    assert load_auto_settings(repo).last_rate_update is not None


@pytest.mark.parametrize("hours", [-1, 721])
def test_invalid_interval(repo, hours):
    with pytest.raises(ValueError):
        save_auto_settings(repo, refresh_hours=hours, auto_rate=False)
