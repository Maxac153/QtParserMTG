import asyncio
import time
from collections.abc import Awaitable, Callable
from urllib.parse import urlsplit

import httpx

from mtgprices.errors import FetchError
from mtgprices.links import validate_link

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
MAX_REDIRECTS = 5
MAX_PAGE_BYTES = 5 * 1024 * 1024
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_RETRY_DELAY = 30.0


class _RetryableError(Exception):
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class Fetcher:
    """Скачивает страницы магазинов.

    - редиректы обрабатываются вручную, чтобы каждый адрес прошёл проверку белого списка;
    - размер ответа ограничен;
    - между запросами к одному сайту выдерживается пауза, временные ошибки повторяются.
    """

    def __init__(
        self,
        timeout: float = 20.0,
        transport: httpx.AsyncBaseTransport | None = None,
        max_bytes: int = MAX_PAGE_BYTES,
        retries: int = 2,
        backoff: float = 2.0,
        min_interval: float = 0.5,
        sleep: Callable[[float], Awaitable[object]] = asyncio.sleep,
    ):
        self.max_bytes = max_bytes
        self.retries = retries
        self.backoff = backoff
        self.min_interval = min_interval
        self._sleep = sleep
        self._host_locks: dict[str, asyncio.Lock] = {}
        self._host_last_request: dict[str, float] = {}
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=False,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.8",
            },
            transport=transport,
        )

    async def fetch(self, url: str) -> str:
        for attempt in range(self.retries + 1):
            try:
                return await self._fetch_once(url)
            except _RetryableError as exc:
                if attempt == self.retries:
                    raise FetchError(str(exc)) from exc
                delay = exc.retry_after if exc.retry_after is not None else self.backoff * 2**attempt
                await self._sleep(min(delay, MAX_RETRY_DELAY))
        raise AssertionError("unreachable")

    async def _fetch_once(self, url: str) -> str:
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            validate_link(current)
            await self._wait_turn(current)
            try:
                async with self._client.stream("GET", current) as response:
                    if response.is_redirect:
                        current = str(response.url.join(response.headers.get("location", "")))
                        continue
                    if response.status_code >= 400:
                        await self._raise_for_status(response, url)
                    return await self._read_text(response, url)
            except httpx.TimeoutException as exc:
                raise _RetryableError(f"Сайт не ответил вовремя: {url}") from exc
            except httpx.TransportError as exc:
                raise _RetryableError(f"Ошибка сети ({type(exc).__name__}): {url}") from exc
            except httpx.HTTPError as exc:
                raise FetchError(f"Ошибка сети ({type(exc).__name__}): {url}") from exc
        raise FetchError(f"Слишком много перенаправлений: {url}")

    async def _wait_turn(self, url: str) -> None:
        """Не чаще одного запроса в min_interval секунд к одному сайту."""
        host = urlsplit(url).hostname or ""
        lock = self._host_locks.setdefault(host, asyncio.Lock())
        async with lock:
            wait = self._host_last_request.get(host, 0.0) + self.min_interval - time.monotonic()
            if wait > 0:
                await self._sleep(wait)
            self._host_last_request[host] = time.monotonic()

    async def _raise_for_status(self, response: httpx.Response, url: str) -> None:
        status = response.status_code
        if status in (403, 503) and _is_cloudflare(response, await self._peek(response)):
            raise FetchError(f"Сайт закрыт проверкой Cloudflare, попробуйте позже или откройте его в браузере: {url}")
        if status in RETRY_STATUSES:
            raise _RetryableError(f"Сайт ответил {status}: {url}", _retry_after(response))
        raise FetchError(f"Сайт ответил {status}: {url}")

    async def _peek(self, response: httpx.Response) -> bytes:
        data = b""
        async for chunk in response.aiter_bytes():
            data += chunk
            if len(data) > 64 * 1024:
                break
        return data

    async def _read_text(self, response: httpx.Response, url: str) -> str:
        chunks = []
        size = 0
        async for chunk in response.aiter_bytes():
            size += len(chunk)
            if size > self.max_bytes:
                raise FetchError(f"Страница слишком большая: {url}")
            chunks.append(chunk)
        encoding = response.encoding or "utf-8"
        return b"".join(chunks).decode(encoding, errors="replace")

    async def aclose(self) -> None:
        await self._client.aclose()


def _is_cloudflare(response: httpx.Response, body: bytes) -> bool:
    if response.headers.get("cf-mitigated") == "challenge":
        return True
    return response.headers.get("server", "").lower() == "cloudflare" and b"Just a moment" in body


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("retry-after", "")
    return float(value) if value.isdigit() else None
