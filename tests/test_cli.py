from decimal import Decimal

import pytest

from mtgprices import __main__ as cli
from mtgprices.config import Settings
from mtgprices.models import Site
from mtgprices.repository import CardRepository
from tests.test_repository import make_legacy_db


def test_import_legacy_command(tmp_path, capsys):
    legacy_dir = tmp_path / "resources"
    legacy_dir.mkdir()
    make_legacy_db(legacy_dir / "cards.db")
    (legacy_dir / "data.config").write_text("DollarExchangeRate: 95\nTables: 1\nSiteList: 1", encoding="utf-8")

    cli.main(["--data-dir", str(tmp_path / "data"), "import-legacy", str(legacy_dir / "cards.db")])

    repo = CardRepository(tmp_path / "data" / "cards.db")
    assert repo.count_by_site() == {Site.STARCITYGAMES: 1, Site.GOLDFISH: 2, Site.SCRYFALL: 0}
    assert repo.get_rate() == Decimal("95.00")
    assert "MTGGoldfish: перенесено 2" in capsys.readouterr().out


def test_import_legacy_missing_file(tmp_path):
    with pytest.raises(SystemExit):
        cli.main(["--data-dir", str(tmp_path), "import-legacy", str(tmp_path / "nope.db")])


def test_legacy_db_is_opened_read_only(tmp_path):
    legacy = tmp_path / "cards.db"
    make_legacy_db(legacy)
    before = legacy.read_bytes()
    repo = CardRepository(tmp_path / "new.db")
    repo.init()
    repo.import_legacy(legacy)
    assert legacy.read_bytes() == before


@pytest.mark.parametrize(
    ("host", "expected"),
    [("127.0.0.1", True), ("localhost", True), ("::1", True), ("0.0.0.0", False), ("192.168.1.5", False)],
)
def test_is_loopback(host, expected):
    assert cli.is_loopback(host) is expected


@pytest.fixture
def captured(monkeypatch):
    captured = {}
    monkeypatch.delenv("MTGPRICES_PASSWORD", raising=False)
    monkeypatch.setattr(
        cli, "serve", lambda settings, open_browser: captured.update(settings=settings, browser=open_browser)
    )
    return captured


def test_serve_arguments(captured, monkeypatch, tmp_path):
    monkeypatch.setenv("MTGPRICES_PASSWORD", "secret")
    cli.main(
        [
            "--data-dir",
            str(tmp_path),
            "--host",
            "0.0.0.0",
            "--port",
            "9000",
            "--no-browser",
            "--allowed-host",
            "192.168.1.5",
        ]
    )
    settings: Settings = captured["settings"]
    assert (settings.host, settings.port, captured["browser"]) == ("0.0.0.0", 9000, False)
    assert "192.168.1.5" in settings.allowed_hosts and "0.0.0.0" not in settings.allowed_hosts
    assert settings.password == "secret"
    monkeypatch.delenv("MTGPRICES_PASSWORD")
    cli.main(["--data-dir", str(tmp_path), "serve"])
    assert captured["settings"].port == 8000 and captured["browser"] is True
    assert captured["settings"].password is None


def test_network_access_requires_password(captured, tmp_path):
    with pytest.raises(SystemExit, match="MTGPRICES_PASSWORD"):
        cli.main(["--data-dir", str(tmp_path), "--host", "0.0.0.0"])
    assert captured == {}
    cli.main(["--data-dir", str(tmp_path), "--host", "0.0.0.0", "--no-password"])
    assert captured["settings"].password is None
