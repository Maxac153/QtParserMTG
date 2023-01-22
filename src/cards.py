import math
from typing import Type

from src.dataBase.data_base import DataBase
from src.table.tables import TableUI
from src.parse.parse import StarCityGamesParse, GoldFishParse
from ui.ui_imagedialog import MyWin
from PyQt5.QtWidgets import QTableWidget


def add_cards(ui: MyWin, cards_number, links, rate, length):
    len_links = len(links)
    len_number_cards = len(cards_number)

    if len_links != len_number_cards:
        ui.BrokenLinks.append(f"Ошибка размера: {len_number_cards}/{len_links}")
        return

    for count in range(length):
        if ui.SiteList.currentText() == "Star City Games":
            try:
                card = StarCityGamesParse(cards_number[count], links[count], rate)
                card.parse()

                try:
                    tabel_bd = DataBase(card.get_data_card())
                    tabel_bd.add_card("Star_City_Games")

                    tabel_ui = TableUI(card.get_data_card())
                    tabel_ui.add_card(ui.TableStarCityGames)
                except Exception:  # тут надо указать какую ошибку хочешь отловить
                    ui.BrokenLinks.append(
                        "Ошибка добавления данных о карте (Уже есть в БД)."
                    )
            except Exception:
                ui.BrokenLinks.append(links[count])

        elif ui.SiteList.currentText() == "Gold Fish":
            try:
                card = GoldFishParse(cards_number[count], links[count], rate)
                card.parse()

                try:
                    tabel_bd = DataBase(card.get_data_card())
                    tabel_bd.add_card("Gold_Fish")

                    tabel_ui = TableUI(card.get_data_card())
                    tabel_ui.add_card(ui.TableGoldFish)
                except Exception:
                    ui.BrokenLinks.append(
                        "Ошибка добавления данных о карте (Уже есть в БД)."
                    )
            except Exception:
                ui.BrokenLinks.append(links[count])
        else:
            ui.BrokenLinks.append("Неизвестный сайт")
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
def get_classes_by_name() -> dict[str, Type[GoldFishParse | StarCityGamesParse]]:
    return {"Star_City_Games": StarCityGamesParse, "Gold_Fish": GoldFishParse}


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
