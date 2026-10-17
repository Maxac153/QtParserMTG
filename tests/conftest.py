from pathlib import Path

import pytest

from mtgprices.errors import FetchError
from mtgprices.repository import CardRepository

FIXTURES = Path(__file__).parent / "fixtures"

SCG_URL = "https://starcitygames.com/prophetic-prism-sgl-mtg-cmr-334-enf/?sku=SGL-MTG-CMR-334-ENF1"
GF_URL = "https://www.mtggoldfish.com/price/The+Brothers+War:Foil/Loran+of+the+Third+Path#paper"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def scg_html() -> str:
    return read_fixture("starcitygames_prophetic_prism_foil.html")


@pytest.fixture(scope="session")
def gf_html() -> str:
    return read_fixture("goldfish_loran_foil.html")


@pytest.fixture(scope="session")
def scryfall_json() -> str:
    return read_fixture("scryfall_loran.json")


class FakeFetcher:
    """Отдаёт сохранённые страницы вместо походов в сеть."""

    def __init__(self, scg_html: str, gf_html: str):
        self.pages = {"starcitygames.com": scg_html, "mtggoldfish.com": gf_html}
        self.pages["api.scryfall.com"] = read_fixture("scryfall_loran.json")
        self.failing: set[str] = set()
        self.requested: list[str] = []

    async def fetch(self, url: str) -> str:
        self.requested.append(url)
        if url in self.failing:
            raise FetchError(f"Сайт ответил 404: {url}")
        for host, html in self.pages.items():
            if host in url:
                return html
        raise AssertionError(f"неожиданный адрес {url}")


@pytest.fixture
def fetcher(scg_html, gf_html) -> FakeFetcher:
    return FakeFetcher(scg_html, gf_html)


@pytest.fixture
def repo(tmp_path) -> CardRepository:
    repo = CardRepository(tmp_path / "cards.db")
    repo.init()
    return repo
