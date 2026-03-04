import math
import re

import pytest
import requests
from bs4 import BeautifulSoup

from src.parse.parse import StarCityGamesParse, GoldFishParse

LINK_STAR_CITY_GAMES = 'https://starcitygames.com/prophetic-prism-sgl-mtg-cmr-334-enf/?sku=SGL-MTG-CMR-334-ENF1'
LINK_GOLD_FISH = 'https://www.mtggoldfish.com/price/The+Brothers+War:Foil/Loran+of+the+Third+Path#paper'


def format_parse(text: str) -> str:
    return re.sub(
        r"\n\n|\n| {2,}|\xa0|\'|\$",
        " ",
        text
    ).strip()


def price_ruble(price_dollar) -> float:
    return math.ceil(price_dollar) * 60


def parse_star_city_games(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    name = format_parse(soup.find('h1', class_='productView-title').text)
    if link[-2] == 'F': name += ' (Foil)'
    name_set = soup.find('title', class_='removeSKU').text.split('|')[1][1:-1]
    price_dollar = float(format_parse(soup.find('span', class_='price price--withoutTax').text))
    price_rouble = price_ruble(price_dollar)
    return 1, name, name_set, price_dollar, price_rouble, link


def parse_gold_fish(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    name = format_parse(soup.find('div', class_='price-card-name-header-name').text[1:-1])
    name_set = format_parse(soup.find('span', class_='price-card-name-set-name').text[1:-1])
    price_dollar = float(format_parse(soup.find('div', class_='price-box-price').text))
    price_rouble = price_ruble(price_dollar)
    return 1, name, name_set, price_dollar, price_rouble, link


def test_parse_card_star_city_games():
    """Проверка парсинга одной карты Star City Games"""
    res1 = parse_star_city_games(LINK_STAR_CITY_GAMES)
    res2 = StarCityGamesParse(link=LINK_STAR_CITY_GAMES)
    res2.parse()
    res2 = res2.get_data_card()
    assert res1 == res2


def test_parse_card_gold_fish():
    """Проверка парсинга одной карты Gold Fish"""
    res1 = parse_gold_fish(LINK_GOLD_FISH)
    res2 = GoldFishParse(link=LINK_GOLD_FISH)
    res2.parse()
    res2 = res2.get_data_card()
    assert res1 == res2


if __name__ == '__main__':
    pytest.main()
