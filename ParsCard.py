#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication, QFileDialog
from threading import Thread

from ui.ui_imagedialog import MyWin
from src.excel.excel import save_to_excel, loding_data_excel
from src.initiation.initiation import loding_data_in_table, loding_data_config
from src.cards import add_cards, recalculation, price_update_cards, price_update_card, remove_card, remove_cards

class Const_tables:
    def __call__(self):
        __tables = {
            'Star_City_Games': ui.TableStarCityGames,
            'Gold_Fish': ui.TableGoldFish
        }
        return __tables

def price_validator():
    price = ui.DollarExchangeRate.text()
    if price.isdigit():
        return price
    return '60'

# Загрузка данных в таблицы
def loding_data():
    tables = Const_tables()()
    for table in tables:
        loding_data_in_table(name_table=table, ui_table=tables[table])

    loding_data_config(ui_rate=ui.DollarExchangeRate, ui_tables=ui.Tables, ui_list=ui.SiteList)

# Добавление карт в UI и DB
def event_add_cards():
    number_cards = ui.NumberCards.toPlainText().split()
    links = ui.LinkCards.toPlainText().split()
    rate = price_validator()
    length = len(number_cards)
    add_cards(ui, number_cards, links, rate, length)

# Создание потока для добавления карт
def thread_add_cards():
    ui.BrokenLinks.clear()
    thread = Thread(target=event_add_cards)
    thread.start()

# Обновление цены на карты
def event_price_update():
    if (ui.Tables.currentIndex() == 0):
        ui_table = ui.TableStarCityGames
        bd_table = 'Star_City_Games'
    elif (ui.Tables.currentIndex() == 1):
        ui_table = ui.TableGoldFish
        bd_table = 'Gold_Fish'
    rate = int(price_validator())
    ui_label = ui.NumberDownloadedLinks
    price_update_cards(ui_table, bd_table, ui_label, price_validator())

# Создание потока для обновление цен
def thread_update_price():
    thread = Thread(target=event_price_update)
    thread.start()

# Перерасчёт цен
def event_price_recalculation():
    rate = price_validator()
    tables = Const_tables()()
    for table in tables:
        recalculation(rate=rate, bd_table=table, ui_table=tables[table])

# Обновление цены одной карты
def event_update_card():
    rate = int(price_validator())
    if (ui.Tables.currentIndex() == 0):
        table = ui.TableStarCityGames
        name_table = 'Star_City_Games'
    elif (ui.Tables.currentIndex() == 1):
        table = ui.TableGoldFish
        name_table = 'Gold_Fish'
    price_update_card(rate, table, name_table)

# Уделение одной карты
def event_remove_card():
    if (ui.Tables.currentIndex() == 0):
        table = ui.TableStarCityGames
        name_table = 'Star_City_Games'
    elif (ui.Tables.currentIndex() == 1):
        table = ui.TableGoldFish
        name_table = 'Gold_Fish'
    remove_card(table, name_table)

# Удаление всех карт из Таблиц
def event_remove_all_cards():
    tables = Const_tables()()
    for table in tables:
        remove_cards(bd_table=table, ui_table=tables[table])

# Сохранение данных в Excel
def event_save_to_excel():
    file_name = QFileDialog.getSaveFileName()[0] + '.xlsx'
    if file_name == '':
        return 0
    save_to_excel(file_name, ui)

# Загрузка данных из Excel
def event_loading_data_excel():
    file_name = QFileDialog.getOpenFileName()[0]
    if file_name == '':
        return 0
    loding_data_excel(file_name, ui)
    thread_add_cards()

# Инцилизация окна приложения
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MyWin()
    loding_data()
    ui.show()

    # Привязка событий к кнопкам
    ui.AddCards.clicked.connect(thread_add_cards)
    ui.PriceReloadedCards.clicked.connect(thread_update_price)
    ui.Recalculation.clicked.connect(event_price_recalculation)
    ui.RemoveAllData.clicked.connect(event_remove_all_cards)
    ui.PriceReloadedCard.clicked.connect(event_update_card)
    ui.RemoveCard.clicked.connect(event_remove_card)
    ui.LoadDataCards.clicked.connect(event_loading_data_excel)
    ui.SaveToExcel.clicked.connect(event_save_to_excel)

    sys.exit(app.exec_())