import asyncio

import httpx
import pytest

from mtgprices.errors import FetchError, InvalidLinkError
from mtgprices.fetcher import Fetcher

URL = "https://www.mtggoldfish.com/price/a"


def fetch(handler, url=URL, sleeps=None, **kwargs):
    """Паузы не ждём по-настоящему, а записываем в sleeps."""
    sleeps = [] if sleeps is None else sleeps

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    kwargs.setdefault("min_interval", 0)

    async def run():
        fetcher = Fetcher(transport=httpx.MockTransport(handler), sleep=fake_sleep, **kwargs)
        try:
            return await fetcher.fetch(url)
        finally:
            await fetcher.aclose()

    return asyncio.run(run())


def test_returns_text_and_sends_user_agent():
    seen = {}

    def handler(request):
        seen["ua"] = request.headers["user-agent"]
        return httpx.Response(200, text="<html>ok</html>")

    assert fetch(handler) == "<html>ok</html>"
    assert "Mozilla" in seen["ua"]


def test_follows_allowed_redirect():
    def handler(request):
        if request.url.host == "www.mtggoldfish.com":
            return httpx.Response(301, headers={"location": "https://mtggoldfish.com/price/a"})
        return httpx.Response(200, text="final")

    assert fetch(handler) == "final"


@pytest.mark.parametrize(
    "location", ["http://127.0.0.1/admin", "http://169.254.169.254/latest/meta-data", "file:///etc"]
)
def test_blocks_redirect_to_other_host(location):
    requested = []

    def handler(request):
        requested.append(str(request.url))
        return httpx.Response(302, headers={"location": location})

    with pytest.raises(InvalidLinkError):
        fetch(handler)
    assert requested == [URL]


def test_redirect_loop():
    with pytest.raises(FetchError, match="перенаправлений"):
        fetch(lambda request: httpx.Response(302, headers={"location": URL}))


def test_http_error_status():
    with pytest.raises(FetchError, match="404"):
        fetch(lambda request: httpx.Response(404))


def test_timeout_and_network_errors_are_retried():
    calls = []

    def timeout(request):
        calls.append(1)
        raise httpx.ReadTimeout("slow", request=request)

    def refused(request):
        raise httpx.ConnectError("refused", request=request)

    sleeps = []
    with pytest.raises(FetchError, match="вовремя"):
        fetch(timeout, sleeps=sleeps, retries=2, backoff=1)
    assert len(calls) == 3
    assert sleeps == [1, 2]
    with pytest.raises(FetchError, match="ConnectError"):
        fetch(refused)


def test_temporary_error_then_success():
    responses = iter(
        [httpx.Response(503), httpx.Response(429, headers={"retry-after": "7"}), httpx.Response(200, text="ok")]
    )
    sleeps = []
    assert fetch(lambda request: next(responses), sleeps=sleeps, backoff=1) == "ok"
    assert sleeps == [1, 7]


def test_retry_after_is_capped():
    sleeps = []
    with pytest.raises(FetchError, match="429"):
        fetch(lambda request: httpx.Response(429, headers={"retry-after": "3600"}), sleeps=sleeps, retries=1)
    assert sleeps == [30.0]


def test_client_errors_are_not_retried():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(404)

    with pytest.raises(FetchError):
        fetch(handler)
    assert len(calls) == 1


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(403, headers={"cf-mitigated": "challenge"}),
        httpx.Response(503, headers={"server": "cloudflare"}, text="<title>Just a moment...</title>"),
    ],
)
def test_cloudflare_challenge_is_reported(response):
    calls = []

    def handler(request):
        calls.append(1)
        return response

    with pytest.raises(FetchError, match="Cloudflare"):
        fetch(handler)
    assert len(calls) == 1


def test_min_interval_between_requests_to_same_host():
    sleeps = []

    async def run():
        async def fake_sleep(seconds):
            sleeps.append(seconds)

        fetcher = Fetcher(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, text="ok")),
            sleep=fake_sleep,
            min_interval=10,
        )
        try:
            await fetcher.fetch(URL)
            await fetcher.fetch("https://starcitygames.com/x")  # другой сайт — без паузы
            await fetcher.fetch(URL)
        finally:
            await fetcher.aclose()

    asyncio.run(run())
    assert len(sleeps) == 1
    assert 9 < sleeps[0] <= 10


def test_page_size_limit():
    with pytest.raises(FetchError, match="большая"):
        fetch(lambda request: httpx.Response(200, content=b"x" * 2000), max_bytes=1000)


def test_rejects_disallowed_url_without_request():
    def handler(request):
        raise AssertionError("запроса быть не должно")

    with pytest.raises(InvalidLinkError):
        fetch(handler, url="http://localhost:8000/")
