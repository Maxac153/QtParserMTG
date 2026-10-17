"""Хранилище в SQLite: карты, история цен, настройки и фоновые задачи.

Все значения передаются в запросы только параметрами.
"""

import json
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from mtgprices.errors import CardNotFoundError, DuplicateCardError, InvalidLinkError
from mtgprices.links import validate_link
from mtgprices.models import Card, ParsedCard, PricePoint, Site

DEFAULT_RATE = Decimal("60")
KEEP_FINISHED_JOBS = 20

# Миграции применяются по порядку; номер последней хранится в PRAGMA user_version
_MIGRATIONS = (
    """
    CREATE TABLE cards (
        id          INTEGER PRIMARY KEY,
        site        TEXT    NOT NULL,
        url         TEXT    NOT NULL,
        quantity    INTEGER NOT NULL CHECK (quantity > 0),
        name        TEXT    NOT NULL,
        set_name    TEXT    NOT NULL,
        price_cents INTEGER,
        updated_at  TEXT,
        last_error  TEXT,
        UNIQUE (site, url)
    );
    CREATE TABLE settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """,
    """
    ALTER TABLE cards ADD COLUMN price_tix_cents INTEGER;
    CREATE TABLE price_history (
        id              INTEGER PRIMARY KEY,
        card_id         INTEGER NOT NULL REFERENCES cards (id) ON DELETE CASCADE,
        checked_at      TEXT,
        price_cents     INTEGER,
        price_tix_cents INTEGER
    );
    CREATE INDEX price_history_card ON price_history (card_id, id);
    INSERT INTO price_history (card_id, checked_at, price_cents)
        SELECT id, updated_at, price_cents FROM cards WHERE price_cents IS NOT NULL;
    CREATE TABLE jobs (
        id         TEXT PRIMARY KEY,
        kind       TEXT NOT NULL,
        title      TEXT NOT NULL,
        status     TEXT NOT NULL,
        created_at TEXT NOT NULL,
        pre_errors TEXT NOT NULL DEFAULT '[]'
    );
    CREATE TABLE job_items (
        job_id  TEXT    NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
        seq     INTEGER NOT NULL,
        payload TEXT    NOT NULL,
        state   TEXT    NOT NULL DEFAULT 'pending',
        error   TEXT,
        PRIMARY KEY (job_id, seq)
    );
    """,
)
SCHEMA_VERSION = len(_MIGRATIONS)

# Таблицы старой Qt-версии (resources/cards.db)
_LEGACY_TABLES = {"StarCityGames": Site.STARCITYGAMES, "GoldFish": Site.GOLDFISH}

_CARD_COLUMNS = """
    c.*,
    (SELECT h.price_cents FROM price_history h WHERE h.card_id = c.id
     ORDER BY h.id DESC LIMIT 1 OFFSET 1) AS previous_price_cents
"""


@dataclass(frozen=True)
class JobRecord:
    id: str
    kind: str
    title: str
    status: str
    created_at: str
    total: int
    done: int
    succeeded: int
    errors: list[str]


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _to_cents(price: Decimal | None) -> int | None:
    return None if price is None else int((price * 100).to_integral_value())


def _from_cents(cents: int | None) -> Decimal | None:
    return None if cents is None else Decimal(cents) / 100


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        id=row["id"],
        site=Site(row["site"]),
        url=row["url"],
        quantity=row["quantity"],
        name=row["name"],
        set_name=row["set_name"],
        price_usd=_from_cents(row["price_cents"]),
        updated_at=row["updated_at"],
        last_error=row["last_error"],
        price_tix=_from_cents(row["price_tix_cents"]),
        previous_price_usd=_from_cents(row["previous_price_cents"]),
    )


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class CardRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            with con:
                yield con
        finally:
            con.close()

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("PRAGMA journal_mode = WAL")
            version = con.execute("PRAGMA user_version").fetchone()[0]
        for number, script in enumerate(_MIGRATIONS[version:], start=version + 1):
            # executescript сам завершает транзакцию, поэтому версия пишется в том же скрипте
            with self._connect() as con:
                con.executescript(f"BEGIN; {script}; PRAGMA user_version = {number}; COMMIT;")

    # --- карты ---

    def add(self, site: Site, url: str, quantity: int, parsed: ParsedCard) -> Card:
        try:
            with self._connect() as con:
                cur = con.execute(
                    """
                    INSERT INTO cards (site, url, quantity, name, set_name, price_cents, price_tix_cents, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        site,
                        url,
                        quantity,
                        parsed.name,
                        parsed.set_name,
                        _to_cents(parsed.price_usd),
                        _to_cents(parsed.price_tix),
                        now_iso(),
                    ),
                )
                card_id = cur.lastrowid
                assert card_id is not None
                self._record_price(con, card_id, parsed)
        except sqlite3.IntegrityError as exc:
            raise DuplicateCardError(f"Карта уже есть в списке: {url}") from exc
        return self.get(card_id)

    def exists(self, site: Site, url: str) -> bool:
        with self._connect() as con:
            row = con.execute("SELECT 1 FROM cards WHERE site = ? AND url = ?", (site, url)).fetchone()
        return row is not None

    def get(self, card_id: int) -> Card:
        with self._connect() as con:
            row = con.execute(f"SELECT {_CARD_COLUMNS} FROM cards c WHERE c.id = ?", (card_id,)).fetchone()
        if row is None:
            raise CardNotFoundError(f"Карта #{card_id} не найдена")
        return _row_to_card(row)

    def list_cards(self, site: Site | None = None, query: str = "") -> list[Card]:
        sql = f"SELECT {_CARD_COLUMNS} FROM cards c WHERE 1 = 1"
        params: list[object] = []
        if site is not None:
            sql += " AND c.site = ?"
            params.append(site)
        if query.strip():
            sql += " AND (c.name LIKE ? ESCAPE '\\' OR c.set_name LIKE ? ESCAPE '\\')"
            pattern = f"%{_escape_like(query.strip())}%"
            params += [pattern, pattern]
        sql += " ORDER BY c.name COLLATE NOCASE, c.id"
        with self._connect() as con:
            return [_row_to_card(row) for row in con.execute(sql, params)]

    def card_ids(self, site: Site | None = None) -> list[int]:
        with self._connect() as con:
            if site is None:
                rows = con.execute("SELECT id FROM cards ORDER BY id")
            else:
                rows = con.execute("SELECT id FROM cards WHERE site = ? ORDER BY id", (site,))
            return [row["id"] for row in rows]

    def count_by_site(self) -> dict[Site, int]:
        counts = dict.fromkeys(Site, 0)
        with self._connect() as con:
            for row in con.execute("SELECT site, COUNT(*) AS n FROM cards GROUP BY site"):
                counts[Site(row["site"])] = row["n"]
        return counts

    def update_from_parsed(self, card_id: int, parsed: ParsedCard) -> Card:
        with self._connect() as con:
            cur = con.execute(
                """
                UPDATE cards
                SET name = ?, set_name = ?, price_cents = ?, price_tix_cents = ?, updated_at = ?, last_error = NULL
                WHERE id = ?
                """,
                (
                    parsed.name,
                    parsed.set_name,
                    _to_cents(parsed.price_usd),
                    _to_cents(parsed.price_tix),
                    now_iso(),
                    card_id,
                ),
            )
            if cur.rowcount == 0:
                raise CardNotFoundError(f"Карта #{card_id} не найдена")
            self._record_price(con, card_id, parsed)
        return self.get(card_id)

    def _record_price(self, con: sqlite3.Connection, card_id: int, parsed: ParsedCard) -> None:
        con.execute(
            "INSERT INTO price_history (card_id, checked_at, price_cents, price_tix_cents) VALUES (?, ?, ?, ?)",
            (card_id, now_iso(), _to_cents(parsed.price_usd), _to_cents(parsed.price_tix)),
        )

    def price_history(self, card_id: int) -> list[PricePoint]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT checked_at, price_cents, price_tix_cents FROM price_history WHERE card_id = ? ORDER BY id",
                (card_id,),
            ).fetchall()
        return [
            PricePoint(row["checked_at"], _from_cents(row["price_cents"]), _from_cents(row["price_tix_cents"]))
            for row in rows
        ]

    def set_error(self, card_id: int, message: str) -> None:
        with self._connect() as con:
            con.execute("UPDATE cards SET last_error = ? WHERE id = ?", (message, card_id))

    def set_quantity(self, card_id: int, quantity: int) -> Card:
        with self._connect() as con:
            cur = con.execute("UPDATE cards SET quantity = ? WHERE id = ?", (quantity, card_id))
        if cur.rowcount == 0:
            raise CardNotFoundError(f"Карта #{card_id} не найдена")
        return self.get(card_id)

    def delete(self, card_id: int) -> None:
        with self._connect() as con:
            con.execute("DELETE FROM cards WHERE id = ?", (card_id,))

    def delete_all(self, site: Site) -> int:
        with self._connect() as con:
            return con.execute("DELETE FROM cards WHERE site = ?", (site,)).rowcount

    # --- настройки ---

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with self._connect() as con:
            row = con.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def get_rate(self) -> Decimal:
        value = self.get_setting("usd_rub_rate")
        return Decimal(value) if value else DEFAULT_RATE

    def set_rate(self, rate: Decimal) -> None:
        self.set_setting("usd_rub_rate", str(rate))

    # --- фоновые задачи ---

    def create_job(self, job_id: str, kind: str, title: str, payloads: Sequence[object], errors: Sequence[str]) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO jobs (id, kind, title, status, created_at, pre_errors) VALUES (?, ?, ?, 'running', ?, ?)",
                (job_id, kind, title, now_iso(), json.dumps(list(errors), ensure_ascii=False)),
            )
            con.executemany(
                "INSERT INTO job_items (job_id, seq, payload) VALUES (?, ?, ?)",
                [(job_id, seq, json.dumps(payload)) for seq, payload in enumerate(payloads)],
            )
            self._prune_jobs(con)

    def pending_job_items(self, job_id: str) -> list[tuple[int, object]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT seq, payload FROM job_items WHERE job_id = ? AND state = 'pending' ORDER BY seq", (job_id,)
            ).fetchall()
        return [(row["seq"], json.loads(row["payload"])) for row in rows]

    def finish_job_item(self, job_id: str, seq: int, error: str | None) -> None:
        with self._connect() as con:
            con.execute(
                "UPDATE job_items SET state = ?, error = ? WHERE job_id = ? AND seq = ?",
                ("error" if error else "ok", error, job_id, seq),
            )

    def set_job_status(self, job_id: str, status: str) -> None:
        with self._connect() as con:
            con.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._connect() as con:
            row = con.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if row is None:
                return None
            return self._job_record(con, row)

    def jobs_with_status(self, status: str) -> list[JobRecord]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM jobs WHERE status = ? ORDER BY created_at", (status,)).fetchall()
            return [self._job_record(con, row) for row in rows]

    def _job_record(self, con: sqlite3.Connection, row: sqlite3.Row) -> JobRecord:
        pre_errors: list[str] = json.loads(row["pre_errors"])
        counts = con.execute(
            """
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(state != 'pending'), 0) AS done,
                   COALESCE(SUM(state = 'ok'), 0) AS succeeded
            FROM job_items WHERE job_id = ?
            """,
            (row["id"],),
        ).fetchone()
        item_errors = [
            r["error"]
            for r in con.execute(
                "SELECT error FROM job_items WHERE job_id = ? AND state = 'error' ORDER BY seq", (row["id"],)
            )
        ]
        return JobRecord(
            id=row["id"],
            kind=row["kind"],
            title=row["title"],
            status=row["status"],
            created_at=row["created_at"],
            total=counts["total"] + len(pre_errors),
            done=counts["done"] + len(pre_errors),
            succeeded=counts["succeeded"],
            errors=pre_errors + item_errors,
        )

    def _prune_jobs(self, con: sqlite3.Connection) -> None:
        con.execute(
            """
            DELETE FROM jobs WHERE status != 'running' AND id NOT IN (
                SELECT id FROM jobs WHERE status != 'running' ORDER BY created_at DESC, rowid DESC LIMIT ?
            )
            """,
            (KEEP_FINISHED_JOBS,),
        )

    # --- перенос данных из Qt-версии ---

    def import_legacy(self, legacy_db: Path) -> dict[Site, int]:
        """Копирует карты из старой БД. Уже существующие и недопустимые ссылки пропускаются."""
        imported = dict.fromkeys(Site, 0)
        legacy = sqlite3.connect(f"file:{legacy_db}?mode=ro", uri=True)
        try:
            existing = {row[0] for row in legacy.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            with self._connect() as con:
                for table, site in _LEGACY_TABLES.items():
                    if table not in existing:
                        continue
                    # Имя таблицы берётся из фиксированного словаря выше
                    rows = legacy.execute(f'SELECT number_card, name, name_set, price_dollar, url FROM "{table}"')
                    for quantity, name, set_name, price, url in rows:
                        if not _legacy_url_ok(str(url or ""), site):
                            continue
                        cents = _legacy_cents(price)
                        cur = con.execute(
                            """
                            INSERT OR IGNORE INTO cards
                                (site, url, quantity, name, set_name, price_cents, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, NULL)
                            """,
                            (site, url, _legacy_quantity(quantity), name, set_name, cents),
                        )
                        if cur.rowcount and cents is not None:
                            # Дата старой цены неизвестна
                            con.execute(
                                "INSERT INTO price_history (card_id, checked_at, price_cents) VALUES (?, NULL, ?)",
                                (cur.lastrowid, cents),
                            )
                        imported[site] += cur.rowcount
        finally:
            legacy.close()
        return imported


def _legacy_url_ok(url: str, site: Site) -> bool:
    try:
        return validate_link(url) is site
    except InvalidLinkError:
        return False


def _legacy_quantity(quantity: object) -> int:
    try:
        return max(int(str(quantity).strip()), 1)
    except ValueError:
        return 1


def _legacy_cents(price: object) -> int | None:
    try:
        return _to_cents(Decimal(str(price)))
    except (ArithmeticError, ValueError):
        return None
