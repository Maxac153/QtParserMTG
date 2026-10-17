import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

APP_NAME = "mtgprices"
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")


def default_data_dir() -> Path:
    """Папка с данными не зависит от текущего каталога запуска."""
    if env := os.environ.get("MTGPRICES_DATA_DIR"):
        return Path(env).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / APP_NAME


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=default_data_dir)
    host: str = "127.0.0.1"
    port: int = 8000
    # Сколько страниц скачивается одновременно
    concurrency: int = 4
    request_timeout: float = 20.0
    # Как часто планировщик проверяет, пора ли обновлять цены и курс; None — выключен
    scheduler_interval: float | None = 60.0
    max_upload_bytes: int = 5 * 1024 * 1024
    # Имена/адреса, по которым сайт открывают с других устройств (при --host 0.0.0.0)
    extra_hosts: tuple[str, ...] = ()
    # Пароль HTTP Basic; обязателен, если сайт доступен из сети
    password: str | None = field(default=None, repr=False)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "cards.db"

    @property
    def allowed_hosts(self) -> list[str]:
        hosts = {"127.0.0.1", "localhost", "[::1]", "::1", *self.extra_hosts}
        if self.host not in ("0.0.0.0", "::"):
            hosts.add(self.host)
        return sorted(hosts)
