import argparse
import ipaddress
import os
import threading
import webbrowser
from pathlib import Path

from mtgprices.config import LOOPBACK_HOSTS, Settings, default_data_dir
from mtgprices.pricing import parse_rate
from mtgprices.repository import CardRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mtgprices", description="Локальный сайт для учёта цен карт MTG")
    parser.add_argument(
        "--data-dir", type=Path, default=None, help=f"папка с данными (по умолчанию {default_data_dir()})"
    )
    commands = parser.add_subparsers(dest="command")

    serve = commands.add_parser("serve", help="запустить сайт (команда по умолчанию)")
    _add_serve_args(serve)
    _add_serve_args(parser)

    legacy = commands.add_parser("import-legacy", help="перенести карты из старой Qt-версии")
    legacy.add_argument("db", type=Path, help="путь к старому resources/cards.db")
    legacy.add_argument("--config", type=Path, default=None, help="старый data.config, чтобы взять курс доллара")
    return parser


def _add_serve_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default="127.0.0.1", help="адрес (по умолчанию только этот компьютер)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="не открывать браузер")
    parser.add_argument(
        "--no-password",
        action="store_true",
        help="разрешить доступ из сети без пароля (пароль задаётся переменной MTGPRICES_PASSWORD)",
    )
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        metavar="HOST",
        help="IP или имя этого компьютера, по которому сайт откроют из сети (можно повторять)",
    )


def is_loopback(host: str) -> bool:
    if host in LOOPBACK_HOSTS:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def serve(settings: Settings, open_browser: bool) -> None:
    import uvicorn

    from mtgprices.web.app import create_app

    if not is_loopback(settings.host):
        print(f"Сайт будет доступен с других устройств по адресу {settings.host}.")
        if not settings.password:
            print("ВНИМАНИЕ: пароля нет, любой в сети сможет менять и удалять карты.")
        if not settings.extra_hosts:
            print("Укажите --allowed-host <IP этого компьютера>, иначе запросы из сети будут отклонены.")
    url = f"http://{'127.0.0.1' if settings.host in ('0.0.0.0', '::') else settings.host}:{settings.port}/"
    print(f"Данные: {settings.db_path}\nСайт: {url}  (остановить — Ctrl+C)")
    if open_browser:
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port, log_level="warning")


def import_legacy(settings: Settings, db: Path, config: Path | None) -> None:
    if not db.is_file():
        raise SystemExit(f"Файл не найден: {db}")
    repo = CardRepository(settings.db_path)
    repo.init()
    counts = repo.import_legacy(db)
    for site, count in counts.items():
        if count:
            print(f"{site.label}: перенесено {count}")
    config = config or db.with_name("data.config")
    if config.is_file():
        rate = read_legacy_rate(config)
        if rate is not None:
            repo.set_rate(rate)
            print(f"Курс доллара: {rate}")
    print(f"Данные сохранены в {settings.db_path}")


def read_legacy_rate(config: Path):
    for line in config.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition(":")
        if key.strip() == "DollarExchangeRate":
            try:
                return parse_rate(value)
            except ValueError:
                return None
    return None


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    data_dir = args.data_dir or default_data_dir()
    if args.command == "import-legacy":
        import_legacy(Settings(data_dir=data_dir), args.db, args.config)
        return
    password = os.environ.get("MTGPRICES_PASSWORD") or None
    if not is_loopback(args.host) and password is None and not args.no_password:
        raise SystemExit(
            "Для доступа из сети задайте пароль в переменной окружения MTGPRICES_PASSWORD "
            "(или явно разрешите вход без пароля флагом --no-password)."
        )
    settings = Settings(
        data_dir=data_dir,
        host=args.host,
        port=args.port,
        extra_hosts=tuple(args.allowed_host),
        password=password,
    )
    serve(settings, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
