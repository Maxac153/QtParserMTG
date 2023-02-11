from bs4 import BeautifulSoup
import requests
import math
import abc


class Parse:
    name: str
    name_set: str
    price_dollar: float
    number_card: int
    url: str
    rate: float
    soup: BeautifulSoup

    def __init__(self, card_number: int = 1, url: str = '', rate: float = 60):
        self.number_card = card_number
        self.url = url
        self.rate = rate
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.text, 'html.parser')

    @abc.abstractmethod
    def parse(self) -> None:
        pass

    @staticmethod
    def _format_parse(text: str) -> str:
        return (
            text.replace('\n\n', ' ')
            .replace('\n', '')
            .replace('  ', '')
            .replace('\xa0', ' ')
            .replace('\'', '')
            .replace('\xa0', ' ')
            .replace('$', '')
        )

    @property
    def price_ruble(self) -> float:
        return math.ceil(self.price_dollar) * self.rate

    def get_data_card(self) -> (str, str, str, float, float, str):
        return (
            self.number_card,
            self.name,
            self.name_set,
            self.price_dollar,
            self.price_ruble,
            self.url,
        )

    def get_data_card_prices(self) -> (float, float):
        return self.price_dollar, self.price_ruble


class StarCityGamesParse(Parse):
    def parse(self) -> (str, str, str, float, float, str):
        self.name = self._format_parse(self.soup.find('h1', class_='productView-title').text)
        if self.url[-2] == 'F': self.name += ' (Foil)'
        self.name_set = self.soup.find('title', class_='removeSKU').text.split('|')[1][1:-1]
        self.price_dollar = float(self._format_parse(self.soup.find('span', class_='price price--withoutTax').text))
        return self.get_data_card()


class GoldFishParse(Parse):
    def parse(self) -> (str, str, str, float, float, str):
        self.name = self._format_parse(self.soup.find('div', class_='price-card-name-header-name').text[1:-1])
        self.name_set = self._format_parse(self.soup.find('span', class_='price-card-name-set-name').text[1:-1])
        self.price_dollar = float(self._format_parse(self.soup.find('div', class_='price-box-price').text))
        return self.get_data_card()
