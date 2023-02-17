#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from enum import IntEnum

from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidget
from threading import Thread, Event

from ui.ui_imagedialog import MyWin
from src.excel.excel import ExcelHandler
from src.initiation.initiation import load_data_in_table, load_data_config
from src.cards import CardManipulator
import time

class Sites(IntEnum):
    Star_City_Games = 0
    Gold_Fish = 1


class Eventor:
    manipulator: CardManipulator
    ui: MyWin
    excel_handler: ExcelHandler

    def __init__(self, ui: MyWin):
        self.ui = ui
        self.manipulator = CardManipulator(self.ui)
        self.excel_handler = ExcelHandler(self.ui)

    def get_site_by_index(self, index: int) -> tuple[str, QTableWidget]:
        ui_table = self.manipulator.get_ui_table_by_name()
        tables = {site.value: (site.name, ui_table[site.name]) for site in Sites}
        return tables[index]

    # Загрузка данных в таблицы
    def load_data(self) -> None:
        ui_by_table_name = self.manipulator.get_ui_table_by_name()
        for table_name, table_ui in ui_by_table_name.items():
            load_data_in_table(table_name=table_name, table_ui=table_ui)

        load_data_config(
            ui_rate=ui.DollarExchangeRate, ui_tables=ui.Tables, ui_list=ui.SiteList
        )

    # Добавление карт в UI и DB
    def _event_add_cards(self, stop_parse) -> None:
        number_cards = ui.NumberCards.toPlainText().split()
        links = ui.LinkCards.toPlainText().split()
        rate = ui.DollarExchangeRate.value()
        length = len(number_cards)
        self.manipulator.add_cards(number_cards, links, rate, length, stop_parse)

    # Создание потока для добавления карт
    def thread_add_cards(self) -> None:
        ui.BrokenLinks.clear()
        thread = Thread(target=self._event_add_cards, args=(stop_parse,))
        thread.start()

    # Обновление цены на карты
    def _event_price_update_all_cards(self) -> None:
        bd_table, ui_table = self.get_site_by_index(ui.Tables.currentIndex())
        rate = ui.DollarExchangeRate.value()
        self.manipulator.update_cards_prices(rate, ui_table)

    # Создание потока для обновление цен
    def thread_update_price_all_cards(self) -> None:
        thread = Thread(target=self._event_price_update_all_cards)
        thread.start()

    # Перерасчёт цен
    def event_price_recalculation(self) -> None:
        rate = ui.DollarExchangeRate.value()
        ui_by_table_name = self.manipulator.get_ui_table_by_name()
        for table_name, ui_table in ui_by_table_name.items():
            self.manipulator.recalculation(rate, ui_table, table_name)

    # Уделение одной карты
    def event_remove_card(self) -> None:
        table_name, ui_table = self.get_site_by_index(ui.Tables.currentIndex())
        self.manipulator.remove_card(ui_table, table_name)

    # Удаление всех карт из Таблиц
    def event_remove_all_cards(self) -> None:
        ui_by_table_name = self.manipulator.get_ui_table_by_name()
        for table_name, ui_table in ui_by_table_name.items():
            self.manipulator.remove_cards(table_name=table_name, ui_table=ui_table)

    # Сохранение данных в Excel
    def event_save_to_excel(self) -> None:
        self.excel_handler.save_to_excel()

    # Загрузка данных из Excel
    def event_load_data_to_excel(self) -> int | None:
        file_name = QFileDialog.getOpenFileName()[0]
        if file_name == "":
            return 0

        self.excel_handler.load_data_from_excel(file_name)
        self.thread_add_cards()

    # Остоновка парсинга
    def event_stop_parse(self):
        stop_parse.set()


# Инцилизация окна приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MyWin()
    eventor = Eventor(ui)
    eventor.load_data()
    ui.show()


    stop_parse = Event()

    # Привязка событий к кнопкам
    ui.AddCards.clicked.connect(eventor.thread_add_cards)
    ui.PriceReloadedCards.clicked.connect(eventor.thread_update_price_all_cards)
    ui.Recalculation.clicked.connect(eventor.event_price_recalculation)
    ui.RemoveAllData.clicked.connect(eventor.event_remove_all_cards)
    ui.RemoveCard.clicked.connect(eventor.event_remove_card)
    ui.LoadDataCards.clicked.connect(eventor.event_load_data_to_excel)
    ui.SaveToExcel.clicked.connect(eventor.event_save_to_excel)
    ui.StopParse.clicked.connect(eventor.event_stop_parse)

    sys.exit(app.exec_())
