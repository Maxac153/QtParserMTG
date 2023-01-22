import math
from typing import Type

from ParseCard import get_ui_table_by_name
from src.dataBase.data_base import DataBase
from src.table.tables import TableUI
from src.parse.parse import StarCityGamesParse, GoldFishParse, Parse
from ui.ui_imagedialog import MyWin
from PyQt5.QtWidgets import QTableWidget


def get_classes_by_name() -> dict[str, Type[GoldFishParse | StarCityGamesParse]]:
    return {"Star_City_Games": StarCityGamesParse, "Gold_Fish": GoldFishParse}


def parse_and_append_to_tables(
    ui: MyWin, card_number: int, link: str, rate: float
) -> None:
    card = Parse()
    card_parses_by_name = get_classes_by_name()
    site_name = ui.SiteList.currentText()
    site_name_with_earth = site_name.replace(" ", "_")
    try:
        card = card_parses_by_name[site_name_with_earth](link, rate, card_number)
        card.parse()
    except Exception:
        ui.BrokenLinks.append(link)

    try:
        card_data = card.get_data_card()
        db_table = DataBase(card_data)
        db_table.add_card(site_name_with_earth)

        ui_table = TableUI(card_data)
        ui_table.add_card(get_ui_table_by_name()[site_name_with_earth])
    except Exception:
        ui.BrokenLinks.append("Ошибка добавления данных о карте (Уже есть в БД).")


def add_cards(
    ui: MyWin, cards_number: list[int], links: list[str], rate: float, length: int
) -> None:
    len_links = len(links)
    len_number_cards = len(cards_number)

    if len_links != len_number_cards:
        ui.BrokenLinks.append(f"Ошибка размера: {len_number_cards}/{len_links}")
        return

    for count in range(length):
        parse_and_append_to_tables(ui, cards_number[count], links[count], rate)
        ui.NumberDownloadedLinks.setText(f"{count + 1}/{length}")


# Изменение цены карт
def recalculation(rate: float, ui_table: QTableWidget, table_name: str):
    rows = ui_table.rowCount()
    for row in range(rows):
        url = ui_table.item(row, 5).text()
        price_dollar = ui_table.item(row, 3).text()
        price_ruble = str(math.ceil(float(price_dollar)) * int(rate))

        table = TableUI(price_ruble)
        table.recalculation(ui_table, row)

        table = DataBase(price_ruble)
        table.recalculation(table_name, url)


# Обновление цены
def update_prices(
    rate: float, row: int, table_name: str, ui_table: QTableWidget, url: str
) -> None:
    classes_by_name = get_classes_by_name()
    card = classes_by_name[table_name](url, rate)
    card.parse()
    data_base = DataBase(card.get_data_card_prices())
    data_base.update_price_card(table_name, url)
    table = TableUI(card.get_data_card_prices())
    table.update_price_card(ui_table, row)


def price_update_card(rate: float, ui_table: QTableWidget, table_name: str) -> None:
    row = ui_table.currentRow()
    if row > -1:
        url = ui_table.item(row, 5).text()
        update_prices(rate, row, table_name, ui_table, url)


# Обновление цен
def update_cards_price(
    rate: float, ui_table: QTableWidget, table_name: str, ui_label: QTableWidget
) -> None:
    rows = ui_table.rowCount()
    for row in range(rows):
        url = ui_table.item(row, 5).text()
        update_prices(rate, row, table_name, ui_table, url)
        ui_label.setText(f"{row + 1}/{rows}")


# Удаление одной карты
def remove_card(ui_table: QTableWidget, table_name: str) -> None:
    row = ui_table.currentRow()
    if row > -1:
        table_db = DataBase(ui_table.item(row, 5).text())
        table_db.remove_cards(table_name)

        table = TableUI()
        table.remove_card(ui_table, row)


# Удаление всех карт
def remove_cards(table_name: str, ui_table: QTableWidget) -> None:
    table = DataBase()
    table.remove_cards(table_name)

    table = TableUI()
    table.remove_cards(ui_table)
