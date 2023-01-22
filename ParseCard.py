#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from enum import IntEnum

from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidget
from threading import Thread

from ui.ui_imagedialog import MyWin
from src.excel.excel import save_to_excel, load_data_from_excel
from src.initiation.initiation import load_data_in_table, load_data_config
from src.cards import (
    add_cards,
    recalculation,
    update_cards_price,
    price_update_card,
    remove_card,
    remove_cards,
)

DOLLAR_DEFAULT_PRICE = "60"


class Sites(IntEnum):
    Star_City_Games = 0
    Gold_Fish = 1


def get_site_by_index(index: int) -> tuple[str, QTableWidget]:
    ui_table = get_ui_table_by_name()
    tables = {site.value: (site.name, ui_table[site.name]) for site in Sites}
    return tables[index]


def get_ui_table_by_name() -> dict[str, QTableWidget]:
    return {"Star_City_Games": ui.TableStarCityGames, "Gold_Fish": ui.TableGoldFish}


def validate_price() -> str:
    price = ui.DollarExchangeRate.text()
    if price.isdigit():
        return price
    return DOLLAR_DEFAULT_PRICE


# Загрузка данных в таблицы
def load_data() -> None:
    ui_by_table_name = get_ui_table_by_name()
    for table_name, table_ui in ui_by_table_name.items():
        load_data_in_table(table_name=table_name, table_ui=table_ui)

    load_data_config(
        ui_rate=ui.DollarExchangeRate, ui_tables=ui.Tables, ui_list=ui.SiteList
    )


# Добавление карт в UI и DB
def event_add_cards() -> None:
    number_cards = ui.NumberCards.toPlainText().split()
    links = ui.LinkCards.toPlainText().split()
    rate = validate_price()
    length = len(number_cards)
    add_cards(ui, number_cards, links, rate, length)


# Создание потока для добавления карт
def thread_add_cards() -> None:
    ui.BrokenLinks.clear()
    thread = Thread(target=event_add_cards)
    thread.start()


# Обновление цены на карты
def event_price_update() -> None:
    bd_table, ui_table = get_site_by_index(ui.Tables.currentIndex())
    rate = float(validate_price())
    ui_label = ui.NumberDownloadedLinks
    update_cards_price(rate, ui_table, bd_table, ui_label)


# Создание потока для обновление цен
def thread_update_price() -> None:
    thread = Thread(target=event_price_update)
    thread.start()


# Перерасчёт цен
def event_price_recalculation() -> None:
    rate = float(validate_price())
    ui_by_table_name = get_ui_table_by_name()
    for table_name, ui_table in ui_by_table_name.items():
        recalculation(rate, ui_table, table_name)


# Обновление цены одной карты
def event_update_card() -> None:
    rate = int(validate_price())
    table_name, ui_table = get_site_by_index(ui.Tables.currentIndex())
    price_update_card(rate, ui_table, table_name)


# Уделение одной карты
def event_remove_card() -> None:
    table_name, ui_table = get_site_by_index(ui.Tables.currentIndex())
    remove_card(ui_table, table_name)


# Удаление всех карт из Таблиц
def event_remove_all_cards() -> None:
    ui_by_table_name = get_ui_table_by_name()
    for table_name, table_ui in ui_by_table_name.items():
        remove_cards(table_name=table_name, ui_table=table_ui)


# Сохранение данных в Excel
def event_save_to_excel() -> int | None:
    file_name = QFileDialog.getSaveFileName()[0] + ".xlsx"
    if file_name == "":
        return 0
    save_to_excel(file_name, ui)


# Загрузка данных из Excel
def event_load_data_to_excel() -> int | None:
    file_name = QFileDialog.getOpenFileName()[0]
    if file_name == "":
        return 0
    load_data_from_excel(file_name, ui)
    thread_add_cards()


# Инцилизация окна приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MyWin()
    load_data()
    ui.show()

    # Привязка событий к кнопкам
    ui.AddCards.clicked.connect(thread_add_cards)
    ui.PriceReloadedCards.clicked.connect(thread_update_price)
    ui.Recalculation.clicked.connect(event_price_recalculation)
    ui.RemoveAllData.clicked.connect(event_remove_all_cards)
    ui.PriceReloadedCard.clicked.connect(event_update_card)
    ui.RemoveCard.clicked.connect(event_remove_card)
    ui.LoadDataCards.clicked.connect(event_load_data_to_excel)
    ui.SaveToExcel.clicked.connect(event_save_to_excel)

    sys.exit(app.exec_())
