"""Проверка ссылок и разбор пользовательского ввода.

Приложение скачивает только страницы известных магазинов: любой другой адрес
(localhost, внутренняя сеть, file://) отклоняется до запроса.
"""

import re
from urllib.parse import urlsplit

from mtgprices.errors import InvalidLinkError
from mtgprices.models import LinkInput, Site

SITE_BY_HOST: dict[str, Site] = {
    "starcitygames.com": Site.STARCITYGAMES,
    "www.starcitygames.com": Site.STARCITYGAMES,
    "mtggoldfish.com": Site.GOLDFISH,
    "www.mtggoldfish.com": Site.GOLDFISH,
    "scryfall.com": Site.SCRYFALL,
    "api.scryfall.com": Site.SCRYFALL,
}

MAX_URL_LENGTH = 2048
MAX_QUANTITY = 10_000

_LINE_RE = re.compile(r"^\s*(?:(\d+)\s*[xх×]?\s+)?(\S+)\s*$", re.IGNORECASE)


def validate_link(url: str) -> Site:
    """Возвращает сайт, к которому относится ссылка, или бросает InvalidLinkError."""
    if len(url) > MAX_URL_LENGTH:
        raise InvalidLinkError("Слишком длинная ссылка")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise InvalidLinkError(f"Некорректная ссылка: {url}") from exc
    if parts.scheme not in ("http", "https"):
        raise InvalidLinkError(f"Ссылка должна начинаться с http(s)://: {url}")
    if parts.username or parts.password or port not in (None, 80, 443):
        raise InvalidLinkError(f"Недопустимая ссылка: {url}")
    site = SITE_BY_HOST.get((parts.hostname or "").lower())
    if site is None:
        raise InvalidLinkError(f"Сайт не поддерживается: {url}")
    return site


def parse_links_text(text: str) -> tuple[list[LinkInput], list[str]]:
    """Разбирает текст вида «3 https://...» по строке на карту.

    Количество можно опустить (тогда 1), допускается «3x ссылка» и табуляция
    (при вставке из Excel). Возвращает корректные строки и сообщения об ошибках.
    """
    items: list[LinkInput] = []
    errors: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        match = _LINE_RE.match(line)
        if match is None:
            errors.append(f"Строка {number}: ожидается «количество ссылка»: {line.strip()}")
            continue
        quantity = int(match.group(1)) if match.group(1) else 1
        url = match.group(2)
        try:
            check_quantity(quantity)
            validate_link(url)
        except InvalidLinkError as exc:
            errors.append(f"Строка {number}: {exc}")
            continue
        items.append(LinkInput(quantity, url))
    return items, errors


def check_quantity(quantity: int) -> int:
    if not 1 <= quantity <= MAX_QUANTITY:
        raise InvalidLinkError(f"Количество должно быть от 1 до {MAX_QUANTITY}")
    return quantity
