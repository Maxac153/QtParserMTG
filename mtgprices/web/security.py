"""Защита локального сайта от запросов со сторонних страниц.

Сайт слушает 127.0.0.1, но любая открытая в браузере вкладка может отправить
форму на localhost (CSRF) или подменить DNS на 127.0.0.1 (DNS rebinding).
Host проверяет TrustedHostMiddleware, а изменяющие запросы должны прийти
с той же страницы (Origin/Referer или Sec-Fetch-Site).
"""

import base64
import binascii
import hmac
from urllib.parse import urlsplit

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    # Не раскрываем адрес локального сайта магазинам при переходе по ссылкам
    "Referrer-Policy": "no-referrer",
}


def is_same_origin(request: Request) -> bool:
    fetch_site = request.headers.get("sec-fetch-site")
    if fetch_site is not None and fetch_site not in ("same-origin", "none"):
        return False
    source = request.headers.get("origin") or request.headers.get("referer")
    if source is None:
        # Нет ни Origin, ни Referer: так ходят curl и скрипты, но не браузерные формы с чужих сайтов
        return fetch_site is None or fetch_site == "none"
    if source == "null":
        return False
    return urlsplit(source).netloc.lower() == request.headers.get("host", "").lower()


class SameOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in SAFE_METHODS and not is_same_origin(request):
            response: Response = PlainTextResponse("Запрос с другого сайта отклонён", status_code=403)
        else:
            response = await call_next(request)
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        return response


class PasswordMiddleware(BaseHTTPMiddleware):
    """HTTP Basic: имя пользователя любое, проверяется только пароль."""

    def __init__(self, app, password: str):
        super().__init__(app)
        self._password = password.encode()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._authorized(request.headers.get("authorization", "")):
            return PlainTextResponse(
                "Нужен пароль",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="MTG Prices", charset="UTF-8"'},
            )
        return await call_next(request)

    def _authorized(self, header: str) -> bool:
        scheme, _, encoded = header.partition(" ")
        if scheme.lower() != "basic":
            return False
        try:
            _, _, password = base64.b64decode(encoded, validate=True).decode().partition(":")
        except (binascii.Error, UnicodeDecodeError):
            return False
        return hmac.compare_digest(password.encode(), self._password)
