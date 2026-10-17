import sqlite3
from decimal import Decimal

import pytest

from mtgprices.errors import CardNotFoundError, DuplicateCardError
from mtgprices.models import ParsedCard, Site
from mtgprices.repository import DEFAULT_RATE, CardRepository

PRISM = ParsedCard("Prophetic Prism (Foil)", "Commander Legends", Decimal("0.35"))
LORAN = ParsedCard("Loran of the Third Path", "The Brothers' War", Decimal("6.96"))


def test_add_and_get(repo):
    card = repo.add(Site.GOLDFISH, "https://www.mtggoldfish.com/a", 3, LORAN)
    assert repo.get(card.id) == card
    assert card.quantity == 3
    assert card.price_usd == Decimal("6.96")
    assert card.updated_at is not None


def test_duplicate_is_rejected_per_site(repo):
    repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    with pytest.raises(DuplicateCardError):
        repo.add(Site.GOLDFISH, "https://x/1", 2, LORAN)
    repo.add(Site.STARCITYGAMES, "https://x/1", 1, PRISM)


def test_list_filters_and_sorts(repo):
    repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    repo.add(Site.STARCITYGAMES, "https://x/2", 1, PRISM)
    repo.add(Site.GOLDFISH, "https://x/3", 1, ParsedCard("abc", "Alpha", Decimal(1)))
    assert [c.name for c in repo.list_cards()] == ["abc", "Loran of the Third Path", "Prophetic Prism (Foil)"]
    assert [c.name for c in repo.list_cards(Site.GOLDFISH)] == ["abc", "Loran of the Third Path"]
    assert [c.name for c in repo.list_cards(query="LORAN")] == ["Loran of the Third Path"]
    assert [c.name for c in repo.list_cards(query="commander")] == ["Prophetic Prism (Foil)"]
    assert repo.count_by_site() == {Site.STARCITYGAMES: 1, Site.GOLDFISH: 2, Site.SCRYFALL: 0}


@pytest.mark.parametrize("query", ["%", "_", '" OR 1=1 --', "'; DROP TABLE cards; --"])
def test_search_special_characters_are_literal(repo, query):
    repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    assert repo.list_cards(query=query) == []
    assert len(repo.list_cards()) == 1


def test_update_quantity_error_delete(repo):
    card = repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    repo.set_error(card.id, "boom")
    assert repo.get(card.id).last_error == "boom"
    updated = repo.update_from_parsed(card.id, ParsedCard("New", "Set", Decimal("1.5")))
    assert (updated.name, updated.price_usd, updated.last_error) == ("New", Decimal("1.5"), None)
    assert repo.set_quantity(card.id, 7).quantity == 7
    repo.delete(card.id)
    with pytest.raises(CardNotFoundError):
        repo.get(card.id)
    with pytest.raises(CardNotFoundError):
        repo.set_quantity(card.id, 1)


def test_delete_all_only_one_site(repo):
    repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    repo.add(Site.STARCITYGAMES, "https://x/2", 1, PRISM)
    assert repo.delete_all(Site.GOLDFISH) == 1
    assert [c.site for c in repo.list_cards()] == [Site.STARCITYGAMES]


def test_rate(repo):
    assert repo.get_rate() == DEFAULT_RATE
    repo.set_rate(Decimal("92.50"))
    repo.set_rate(Decimal("95.00"))
    assert repo.get_rate() == Decimal("95.00")


def test_init_is_idempotent(tmp_path):
    repo = CardRepository(tmp_path / "nested" / "cards.db")
    repo.init()
    repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    repo.init()
    assert len(repo.list_cards()) == 1


def make_legacy_db(path):
    con = sqlite3.connect(path)
    for table in ("GoldFish", "StarCityGames"):
        con.execute(
            f'CREATE TABLE "{table}" (number_card TEXT, name TEXT, name_set TEXT, '
            "price_dollar TEXT, price_ruble TEXT, url TEXT, PRIMARY KEY(url))"
        )
    con.executemany(
        "INSERT INTO GoldFish VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("3", "Smothering Tithe", "Promos", "75.94", "4560", "https://www.mtggoldfish.com/a#paper"),
            ("x", "Bad qty", "Set", "oops", "", "https://www.mtggoldfish.com/b"),
        ],
    )
    con.execute("INSERT INTO StarCityGames VALUES ('1', 'Prism', 'CMR', '0.35', '60', 'https://starcitygames.com/p')")
    con.execute("INSERT INTO StarCityGames VALUES ('1', 'XSS', 'S', '1', '60', 'javascript:alert(1)')")
    con.execute("INSERT INTO StarCityGames VALUES ('1', 'Wrong', 'S', '1', '60', 'https://www.mtggoldfish.com/c')")
    con.commit()
    con.close()


def test_import_legacy(repo, tmp_path):
    legacy = tmp_path / "legacy.db"
    make_legacy_db(legacy)
    assert repo.import_legacy(legacy) == {Site.GOLDFISH: 2, Site.STARCITYGAMES: 1, Site.SCRYFALL: 0}
    tithe, bad = repo.list_cards(Site.GOLDFISH, "")[1], repo.list_cards(Site.GOLDFISH, "")[0]
    assert (tithe.quantity, tithe.price_usd) == (3, Decimal("75.94"))
    assert (bad.quantity, bad.price_usd) == (1, None)
    # Повторный импорт ничего не дублирует
    assert repo.import_legacy(legacy) == {Site.GOLDFISH: 0, Site.STARCITYGAMES: 0, Site.SCRYFALL: 0}


def test_price_history_and_previous_price(repo):
    card = repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    assert card.previous_price_usd is None
    repo.update_from_parsed(card.id, ParsedCard("Loran", "BRO", Decimal("7.50"), Decimal("1.2")))
    updated = repo.update_from_parsed(card.id, ParsedCard("Loran", "BRO", Decimal("8.00")))
    assert (updated.price_usd, updated.previous_price_usd, updated.price_tix) == (Decimal("8"), Decimal("7.5"), None)
    history = repo.price_history(card.id)
    assert [p.price_usd for p in history] == [Decimal("6.96"), Decimal("7.5"), Decimal("8")]
    assert history[1].price_tix == Decimal("1.2")
    assert repo.list_cards()[0].previous_price_usd == Decimal("7.5")
    # История удаляется вместе с картой
    repo.delete(card.id)
    assert repo.price_history(card.id) == []


def test_migration_from_schema_v1(tmp_path):
    from mtgprices.repository import _MIGRATIONS, SCHEMA_VERSION

    path = tmp_path / "cards.db"
    con = sqlite3.connect(path)
    con.executescript(_MIGRATIONS[0])
    con.execute(
        "INSERT INTO cards (site, url, quantity, name, set_name, price_cents, updated_at) "
        "VALUES ('goldfish', 'https://x/1', 2, 'Old', 'Set', 123, '2026-01-01T00:00:00+00:00')"
    )
    con.execute("PRAGMA user_version = 1")
    con.commit()
    con.close()

    repo = CardRepository(path)
    repo.init()
    card = repo.list_cards()[0]
    assert (card.name, card.price_usd, card.price_tix) == ("Old", Decimal("1.23"), None)
    assert [p.price_usd for p in repo.price_history(card.id)] == [Decimal("1.23")]
    con = sqlite3.connect(path)
    assert con.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    con.close()


def test_settings(repo):
    assert repo.get_setting("missing") is None
    assert repo.get_setting("missing", "x") == "x"
    repo.set_setting("k", "1")
    repo.set_setting("k", "2")
    assert repo.get_setting("k") == "2"


def test_card_ids(repo):
    a = repo.add(Site.GOLDFISH, "https://x/1", 1, LORAN)
    b = repo.add(Site.STARCITYGAMES, "https://x/2", 1, PRISM)
    assert repo.card_ids() == [a.id, b.id]
    assert repo.card_ids(Site.STARCITYGAMES) == [b.id]


def test_job_store(repo):
    repo.create_job("j1", "add", "Тест", [{"url": "u"}, 7], ["ошибка ввода"])
    job = repo.get_job("j1")
    assert (job.total, job.done, job.succeeded, job.status) == (3, 1, 0, "running")
    repo.finish_job_item("j1", 0, None)
    repo.finish_job_item("j1", 1, "сбой")
    job = repo.get_job("j1")
    assert (job.done, job.succeeded, job.errors) == (3, 1, ["ошибка ввода", "сбой"])
    assert repo.pending_job_items("j1") == []
    assert repo.get_job("nope") is None


def test_legacy_import_records_history_without_date(repo, tmp_path):
    legacy = tmp_path / "legacy.db"
    make_legacy_db(legacy)
    repo.import_legacy(legacy)
    card = next(c for c in repo.list_cards() if c.name == "Smothering Tithe")
    assert [(p.checked_at, p.price_usd) for p in repo.price_history(card.id)] == [(None, Decimal("75.94"))]
