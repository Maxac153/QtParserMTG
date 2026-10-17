import pytest

from mtgprices.errors import InvalidLinkError
from mtgprices.links import parse_links_text, validate_link
from mtgprices.models import LinkInput, Site
from tests.conftest import GF_URL, SCG_URL


def test_validate_known_sites():
    assert validate_link(SCG_URL) is Site.STARCITYGAMES
    assert validate_link(GF_URL) is Site.GOLDFISH
    assert validate_link("http://MTGGOLDFISH.com/price/x") is Site.GOLDFISH


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://localhost/admin",
        "file:///etc/passwd",
        "https://evil.example/www.mtggoldfish.com",
        "https://www.mtggoldfish.com.evil.example/",
        "https://user:pass@www.mtggoldfish.com/",
        "https://www.mtggoldfish.com:8080/",
        "https://www.mtggoldfish.com:99999/",
        "javascript:alert(1)",
        "https://www.mtggoldfish.com/" + "a" * 3000,
    ],
)
def test_rejects_other_hosts(url):
    with pytest.raises(InvalidLinkError):
        validate_link(url)


def test_parse_links_text():
    text = f"""
    3 {GF_URL}
    {SCG_URL}
    2x {GF_URL}?b
    4\t{GF_URL}?c
    0 {GF_URL}?d
    5 http://127.0.0.1/
    один два три
    """
    items, errors = parse_links_text(text)
    assert items == [
        LinkInput(3, GF_URL),
        LinkInput(1, SCG_URL),
        LinkInput(2, GF_URL + "?b"),
        LinkInput(4, GF_URL + "?c"),
    ]
    assert len(errors) == 3
    assert errors[0].startswith("Строка 6:")
