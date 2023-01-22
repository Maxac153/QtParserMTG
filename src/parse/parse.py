import abc

from bs4 import BeautifulSoup
import requests


class Parse:
    name: str
    name_set: str
    price_dollar: float
    number_card: int
    url: str
    rate: float
    soup: BeautifulSoup

    @property
    def price_ruble(self) -> float:
        return self.price_dollar * self.rate

    def __init__(self, url: str = "", rate: float = 0, card_number: int = 0):
        self.number_card = card_number
        self.url = url
        self.rate = rate
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.text, "html.parser")

    @abc.abstractmethod
    def parse(self) -> None:
        ...

    @staticmethod
    def _format_after_parse(text: str) -> str:
        return (
            text.replace("\n\n", " ")
            .replace("\n", "")
            .replace("  ", "")
            .replace("\xa0", " ")
            .replace("'", "")
            .replace("\xa0", " ")
        )

    def get_data_card(self):
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
    # Парсинг данных с Star City Games
    def parse(self) -> None:
        self.name = self._format_after_parse(
            self.soup.find("h1", class_="productView-title").text
        )
        if self.url[-2] == "F":
            self.name += " (Foil)"
        self.name_set = self.soup.find("title", class_="removeSKU").text.split("|")[1][
            1:-1
        ]
        self.price_dollar = float(
            self.soup.find("span", class_="price price--withoutTax").text[1:]
        )


class GoldFishParse(Parse):
    # Парсинг данных с Gold Fish
    def parse(self) -> None:
        self.name = self._format_after_parse(
            self.soup.find("div", class_="price-card-name-header-name").text[1:-1]
        )
        self.name_set = self._format_after_parse(
            self.soup.find("span", class_="price-card-name-set-name").text[1:-1]
        )
        self.price_dollar = float(
            self.soup.find("div", class_="price-box-price").text[2:]
        )
