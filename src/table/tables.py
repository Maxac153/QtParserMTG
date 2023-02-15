from PyQt5 import QtWidgets


class TableUI:
    @staticmethod
    def add_card(data_card, ui_table):
        row_position = ui_table.rowCount()
        ui_table.insertRow(row_position)

        for i in range(len(data_card)):
            ui_table.setItem(row_position, i, QtWidgets.QTableWidgetItem(str(data_card[i])))

    @staticmethod
    def update_price_cards(data_card, ui_table):
        row_position = ui_table.rowCount()

        for i in range(row_position):
            ui_table.item(i, 3).setText(str(data_card[3]))
            ui_table.item(i, 4).setText(str(data_card[4]))

    @staticmethod
    def recalculation(data_card, ui_table, row):
        ui_table.setItem(row, 4, QtWidgets.QTableWidgetItem(data_card))

    @staticmethod
    def remove_card(ui_table, row):
        ui_table.removeRow(row)
        ui_table.selectionModel().clearCurrentIndex()

    @staticmethod
    def remove_cards(ui_table):
        ui_table.setRowCount(0)

    @staticmethod
    def load_data_card(data_card, ui_table):
        for item in data_card:
            row_position = ui_table.rowCount()
            ui_table.insertRow(row_position)

            for i in range(len(item)):
                ui_table.setItem(row_position, i, QtWidgets.QTableWidgetItem(item[i]))
