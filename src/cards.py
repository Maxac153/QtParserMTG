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

    def get_ui_table_by_name(self) -> dict[str, QTableWidget]:
        return {
            "Star_City_Games": self.ui.TableStarCityGames,
            "Gold_Fish": self.ui.TableGoldFish,
        }

    @staticmethod
    def _get_classes_by_name() -> dict[str, Type[GoldFishParse | StarCityGamesParse]]:
        return {"Star_City_Games": StarCityGamesParse, "Gold_Fish": GoldFishParse}

    @classmethod
    def parse_cards(self, args):
        card_number, link, rate, f = args
        try:
            card = f(card_number, link, rate)
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
                    card_data = data_card
                    db_table = DataBase(card_data)
                    db_table.add_card(site_name_with_earth)

                    ui_table = TableUI(card_data)
                    ui_table.add_card(self.get_ui_table_by_name()[site_name_with_earth])
                except Exception:
                    self.ui.BrokenLinks.append(
                        "Ошибка добавления данных о карте (Уже есть в БД)."
                    )

    def add_cards(
            self, cards_number: list[int], links: list[str], rate: float, length: int
    ) -> None:
        len_links = len(links)
        len_number_cards = len(cards_number)

        card_parses_by_name = self._get_classes_by_name()
        site_name = self.ui.SiteList.currentText()
        site_name_with_earth = site_name.replace(" ", "_")

        if len_links != len_number_cards:
            self.ui.BrokenLinks.append(
                f"Ошибка размера: {len_number_cards}/{len_links}"
            )
            return

        data = [(cards_number[i], links[i], rate, card_parses_by_name[site_name_with_earth]) for i in range(len(links))]
        cpu_core = os.cpu_count()
        pool = multiprocessing.Pool(processes=cpu_core)

        if length >= cpu_core:
            for i in range(length // cpu_core):
                data_card = data[i * cpu_core: i * cpu_core + cpu_core]
                data_cards = pool.map(self.parse_cards, data_card)
                self.add_data_cards_tabel(site_name_with_earth, data_cards)
                self.ui.NumberDownloadedLinks.setText(f'{length}/{i * cpu_core + cpu_core}')

        rest = length % cpu_core
        if rest != 0:
            data_card = data[-(length % cpu_core):]
            data_cards = pool.map(self.parse_cards, data_card)
            self.add_data_cards_tabel(site_name_with_earth, data_cards)
            self.ui.NumberDownloadedLinks.setText(f'{length}/{length // cpu_core * cpu_core + rest}')

    # Изменение цены карт
    def recalculation(self, rate: float, ui_table: QTableWidget, table_name: str):
        rows = ui_table.rowCount()
        for row in range(rows):
            url = ui_table.item(row, 5).text()
            price_dollar = ui_table.item(row, 3).text()
            price_ruble = str(math.ceil(float(price_dollar)) * int(rate))

            self.desktop_table = TableUI(price_ruble)
            self.desktop_table.recalculation(ui_table, row)

            self.database = DataBase(price_ruble)
            self.database.recalculation(table_name, url)

    # Обновление цены
    def update_prices(
            self, rate: float, row: int, table_name: str, ui_table: QTableWidget, url: str
    ) -> None:
        classes_by_name = self._get_classes_by_name()
        card = classes_by_name[table_name](url, rate)
        card.parse()
        data_base = DataBase(card.get_data_card_prices())
        data_base.update_price_card(table_name, url)
        table = TableUI(card.get_data_card_prices())
        table.update_price_card(ui_table, row)

    def price_update_card(
            self, rate: float, ui_table: QTableWidget, table_name: str
    ) -> None:
        row = ui_table.currentRow()
        if row > -1:
            url = ui_table.item(row, 5).text()
            self.update_prices(rate, row, table_name, ui_table, url)

    # Обновление цен
    def update_cards_price(
            self,
            rate: float,
            ui_table: QTableWidget,
            table_name: str,
            ui_label: QTableWidget,
    ) -> None:
        rows = ui_table.rowCount()
        for row in range(rows):
            url = ui_table.item(row, 5).text()
            self.update_prices(rate, row, table_name, ui_table, url)
            ui_label.setText(f"{row + 1}/{rows}")

    # Удаление одной карты
    def remove_card(self, ui_table: QTableWidget, table_name: str) -> None:
        row = ui_table.currentRow()
        if row > -1:
            self.database = DataBase(ui_table.item(row, 5).text())
            self.database.remove_cards(table_name)

            self.desktop_table.remove_card(ui_table, row)

    # Удаление всех карт
    def remove_cards(self, table_name: str, ui_table: QTableWidget) -> None:
        self.database.remove_cards(table_name)
        self.desktop_table.remove_cards(ui_table)
