import math
from typing import Type

from src.dataBase.data_base import DataBase
from src.table.tables import TableUI
from src.parse.parse import StarCityGamesParse, GoldFishParse, Parse
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

    def _parse_and_append_to_tables(
        self, card_number: int, link: str, rate: float
    ) -> None:
        try:
            Parse(url=link, rate=rate, card_number=card_number)
            card_parses_by_name = self._get_classes_by_name()
            site_name = self.ui.SiteList.currentText()
            site_name_with_earth = site_name.replace(" ", "_")

            card = card_parses_by_name[site_name_with_earth](link, rate, card_number)
            card.parse()

            try:
                card_data = card.get_data_card()
                db_table = DataBase(card_data)
                db_table.add_card(site_name_with_earth)

                ui_table = TableUI(card_data)
                ui_table.add_card(self.get_ui_table_by_name()[site_name_with_earth])
            except Exception:
                self.ui.BrokenLinks.append(
                    "Ошибка добавления данных о карте (Уже есть в БД)."
                )

        except Exception:
            self.ui.BrokenLinks.append(link)



    def add_cards(
        self, cards_number: list[int], links: list[str], rate: float, length: int
    ) -> None:
        len_links = len(links)
        len_number_cards = len(cards_number)

        if len_links != len_number_cards:
            self.ui.BrokenLinks.append(
                f"Ошибка размера: {len_number_cards}/{len_links}"
            )
            return

        for count in range(length):
            self._parse_and_append_to_tables(cards_number[count], links[count], rate)
            self.ui.NumberDownloadedLinks.setText(f"{count + 1}/{length}")

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
