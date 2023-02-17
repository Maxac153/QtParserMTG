import math
import os
import multiprocessing
from typing import Type

from src.dataBase.data_base import DataBase
from src.table.tables import TableUI
from src.parse.parse import StarCityGamesParse, GoldFishParse
from ui.ui_imagedialog import MyWin
from PyQt5.QtWidgets import QTableWidget


class CardManipulator:
    ui: MyWin

    def __init__(self, ui: MyWin):
        self.ui = ui
        self.database = DataBase()
        self.desktop_table = TableUI()
        self.cpu_core = os.cpu_count()

    def get_ui_table_by_name(self) -> dict[str, QTableWidget]:
        return {
            "Star_City_Games": self.ui.TableStarCityGames,
            "Gold_Fish": self.ui.TableGoldFish,
        }

    @staticmethod
    def _get_classes_by_name() -> dict[str, Type[GoldFishParse | StarCityGamesParse]]:
        return {"Star_City_Games": StarCityGamesParse, "Gold_Fish": GoldFishParse}

    @staticmethod
    def parse_cards(args):
        card_number, link, rate, card_parses_by_name = args
        try:
            card = card_parses_by_name(card_number, link, rate)
            data_cards = card.parse()
            return data_cards
        except Exception:
            return f'Битая ссылка: {link}'

    def add_data_cards_tabel(self, site_name_with_earth, data_cards):
        for data_card in data_cards:
            if type(data_card) == str:
                self.ui.BrokenLinks.append(data_card)
            else:
                try:
                    self.database_method(data_card, site_name_with_earth)
                    self.table_method(data_card, self.get_ui_table_by_name()[site_name_with_earth])
                except Exception:
                    self.ui.BrokenLinks.append(
                        f"Ошибка добавления данных о карте (Уже есть в БД): {data_card[-1]}."
                    )

    # Добавление карты и обновление цен
    def parse(self, cards_number, links, rate, length, stop_parse):
        len_links = len(links)
        len_number_cards = len(cards_number)

        site_name = self.ui.SiteList.currentText()
        site_name_with_earth = site_name.replace(" ", "_")
        card_parses_by_name = self._get_classes_by_name()[site_name_with_earth]

        if len_links != len_number_cards:
            self.ui.BrokenLinks.append(
                f"Ошибка размера: {len_number_cards}/{len_links}"
            )
            return

        data = [(cards_number[i], links[i], rate, card_parses_by_name) for i in range(len(links))]
        pool = multiprocessing.Pool(processes=self.cpu_core)

        if length >= self.cpu_core:
            for i in range(length // self.cpu_core):
                if stop_parse.is_set():
                    stop_parse.clear()
                    return

                data_card = data[i * self.cpu_core: i * self.cpu_core + self.cpu_core]
                data_cards = pool.map(self.parse_cards, data_card)
                self.add_data_cards_tabel(site_name_with_earth, data_cards)
                self.ui.NumberDownloadedLinks.setText(f'{length}/{i * self.cpu_core + self.cpu_core}')

        rest = length % self.cpu_core
        if rest != 0:
            data_card = data[-(length % self.cpu_core):]
            data_cards = pool.map(self.parse_cards, data_card)
            self.add_data_cards_tabel(site_name_with_earth, data_cards)
            self.ui.NumberDownloadedLinks.setText(f'{length}/{length // self.cpu_core * self.cpu_core + rest}')

    def add_cards(
            self, cards_number: list[int], links: list[str], rate: int, length: int, stop_parse
    ) -> None:
        self.database_method = DataBase.add_card
        self.table_method = TableUI.add_card
        self.parse(cards_number, links, rate, length, stop_parse)

    # Обновить цену всех карт
    def update_cards_prices(
            self, rate: int, ui_table: QTableWidget,
    ) -> None:
        rows = ui_table.rowCount()
        self.database_method = DataBase.update_price_card
        self.table_method = TableUI.update_price_cards

        links = []
        cards_number = []
        for row in range(rows):
            cards_number.append(int(ui_table.item(row, 0).text()))
            links.append(ui_table.item(row, 5).text())
        length = len(cards_number)
        self.parse(cards_number, links, rate, length)

    # Изменение цены карт
    def recalculation(self, rate: int, ui_table: QTableWidget, table_name: str):
        rows = ui_table.rowCount()
        for row in range(rows):
            url = ui_table.item(row, 5).text()
            price_dollar = ui_table.item(row, 3).text()
            price_ruble = str(math.ceil(float(price_dollar)) * int(rate))

            TableUI.recalculation(price_ruble, ui_table, row)
            DataBase.recalculation(price_ruble, table_name, url)

    # Удаление одной карты
    def remove_card(self, ui_table: QTableWidget, table_name: str) -> None:
        row = ui_table.currentRow()
        if row > -1:
            data_card = ui_table.item(row, 5).text()
            DataBase.remove_card(data_card, table_name)
            TableUI.remove_card(ui_table, row)

    # Удаление всех карт
    def remove_cards(self, table_name: str, ui_table: QTableWidget) -> None:
        self.database.remove_cards(table_name)
        self.desktop_table.remove_cards(ui_table)
