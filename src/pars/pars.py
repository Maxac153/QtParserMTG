from bs4 import BeautifulSoup
import requests
import math

class Pars:
    name = ''
    name_set = ''
    price_dollar = ''
    price_ruble = ''

    def __init__(self, number_card=0, url='', rate=0):
        self.number_card = number_card
        self.url = url
        self.rate = rate
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.text, "html.parser")

    def get_data_card(self):
        return (
            self.number_card,
            Pars.name,
            Pars.name_set,
            Pars.price_dollar,
            Pars.price_ruble,
            self.url
        )

    def get_data_card_price(self):
        return (
            Pars.price_dollar,
            Pars.price_ruble
        )

class ParsingStarCityGames(Pars):
    # Парсинг данных с Star City Games
    def parse_star_city_games(self):
        Pars.name = self.soup.find('h1', class_='productView-title').text \
            .replace('\n\n', ' ') \
            .replace('\n', '') \
            .replace('  ', '') \
            .replace('\xa0', ' ') \
            .replace('\'', '')
        if self.url[-2] == 'F':
            Pars.name += ' (Foil)'
        Pars.name_set = self.soup.find('title', class_='removeSKU').text.split('|')[1][1:-1]
        self.parse_star_city_games_price()

    # Обновление цены с Star City Games
    def parse_star_city_games_price(self):
        Pars.price_dollar = self.soup.find('span', class_='price price--withoutTax').text[1:]
        Pars.price_ruble = str(math.ceil(float(Pars.price_dollar)) * int(self.rate))

class ParsingGoldFish(Pars):
    # Парсинг данных с Gold Fish
    def parse_gold_fish(self):
        Pars.name = self.soup.find('div', class_='price-card-name-header-name').text[1:-1] \
            .replace('\n\n', ' ') \
            .replace('\n', '') \
            .replace('\xa0', ' ') \
            .replace('\'', '')
        Pars.name_set = self.soup.find('span', class_='price-card-name-set-name').text[1:-1] \
            .replace('\xa0', ' ').replace('\'', ' ')
        self.parse_gold_fish_price()

    # Обновление цены c Gold Fish
    def parse_gold_fish_price(self):
        Pars.price_dollar = self.soup.find('div', class_='price-box-price').text[2:]
        Pars.price_ruble = str(math.ceil(float(Pars.price_dollar)) * int(self.rate))