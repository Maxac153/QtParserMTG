from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget


class TableUI:
    def __init__(self, data_card=()):
        self.data_card = data_card

    def add_card(self, ui_table) -> None:
        row_position = ui_table.rowCount()
        ui_table.insertRow(row_position)

        for i in range(len(self.data_card)):
            ui_table.setItem(row_position, i, QtWidgets.QTableWidgetItem(str(self.data_card[i])))

    def remove_card(self, ui_table, row) -> None:
        ui_table.removeRow(row)
        ui_table.selectionModel().clearCurrentIndex()

    def remove_cards(self, ui_table) -> None:
        ui_table.setRowCount(0)

    def update_price_card(self, ui_table, row) -> None:
        ui_table.item(row, 3).setText(str(self.data_card[0]))
        ui_table.item(row, 4).setText(str(self.data_card[1]))

    def recalculation(self, ui_table, row) -> None:
        ui_table.setItem(row, 4, QtWidgets.QTableWidgetItem(self.data_card))

    def load_data_card(self, ui_table) -> None:
        for item in self.data_card:
            row_position = ui_table.rowCount()
            ui_table.insertRow(row_position)

            for i in range(len(item)):
                ui_table.setItem(row_position, i, QtWidgets.QTableWidgetItem(item[i]))
