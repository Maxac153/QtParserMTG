import math
import sqlite3 as sq
from PyQt5 import QtWidgets

from src.dataBase.data_base import DataBase
from src.table.tables import TablesUI
from src.pars.pars import ParsingStarCityGames, ParsingGoldFish

def add_cards(ui, number_cards, links, rate, length):
    len_links = len(links)
    len_number_cards = len(number_cards)

    if len_links != len_number_cards:
        ui.BrokenLinks.append(f'Ошибка размера: {len_number_cards}/{len_links}')
        return

    for count in range(length):
        if ui.SiteList.currentText() == 'Star City Games':
            try:
                card = ParsingStarCityGames(number_cards[count], links[count], rate)
                card.parse_star_city_games()

                try:
                    tabelBD = DataBase(card.get_data_card())
                    tabelBD.add_card('Star_City_Games')

                    tabelUi = TablesUI(card.get_data_card())
                    tabelUi.add_card(ui.TableStarCityGames)
                except:
                    ui.BrokenLinks.append('Ошибка добавления данных о карте (Уже есть в БД).')
            except:
                ui.BrokenLinks.append(links[count])

        elif ui.SiteList.currentText() == 'Gold Fish':
            try:
                card = ParsingGoldFish(number_cards[count], links[count], rate)
                card.parse_gold_fish()

                try:
                    tabelBD = DataBase(card.get_data_card())
                    tabelBD.add_card('Gold_Fish')

                    tabelUi = TablesUI(card.get_data_card())
                    tabelUi.add_card(ui.TableGoldFish)
                except:
                    ui.BrokenLinks.append('Ошибка добавления данных о карте (Уже есть в БД).')
            except:
                ui.BrokenLinks.append(links[count])

        ui.NumberDownloadedLinks.setText(f'{count + 1}/{length}')

# Изменение цены карт
def recalculation(rate, ui_table, bd_table):
    rows = ui_table.rowCount()
    for row in range(rows):
        url = ui_table.item(row, 5).text()
        price_dollar = ui_table.item(row, 3).text()
        price_ruble = str(math.ceil(float(price_dollar)) * int(rate))

        table = TablesUI((price_ruble))
        table.recalculation(ui_table=ui_table, row=row)

        table = DataBase((price_ruble))
        table.recalculation(name_table=bd_table, url=url)

# Обновление цены
def price_update_card(rate, ui_table, bd_table):
    row = ui_table.currentRow()
    if row > -1:
        url = ui_table.item(row, 5).text()

        if bd_table == 'Star_City_Games':
            card = ParsingStarCityGames(url=url, rate=rate)
            card.parse_star_city_games_price()
        elif bd_table == 'Gold_Fish':
            card = ParsingGoldFish(url=url, rate=rate)
            card.parse_gold_fish_price()

        data_base = DataBase(card.get_data_card_price())
        data_base.update_price_card(bd_table, url)

        table = TablesUI(card.get_data_card_price())
        table.update_price_card(ui_table, row)

# Обновление цен
def price_update_cards(ui_table, bd_table, ui_label, rate):
    rows = ui_table.rowCount()
    for row in range(rows):
        url = ui_table.item(row, 5).text()

        if bd_table == 'Star_City_Games':
            card = ParsingStarCityGames(url=url, rate=rate)
            card.parse_star_city_games_price()
        elif bd_table == 'Gold_Fish':
            card = ParsingGoldFish(url=url, rate=rate)
            card.parse_gold_fish_price()

        data_base = DataBase(card.get_data_card_price())
        data_base.update_price_card(bd_table, url)

        table = TablesUI(card.get_data_card_price())
        table.update_price_card(ui_table, row)

        ui_label.setText(f'{row + 1}/{rows}')

# Удаление одной карты
def remove_card(ui_table, name_table):
    row = ui_table.currentRow()
    if row > -1:
        table_db = DataBase(ui_table.item(row, 5).text())
        table_db.remove_cards(name_table)

        table = TablesUI()
        table.remove_card(ui_table, row)

# Удаление всех карт
def remove_cards(bd_table, ui_table):
    table = DataBase()
    table.remove_cards(bd_table)

    table = TablesUI()
    table.remove_cards(ui_table)