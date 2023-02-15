from src.dataBase.data_base import DataBase
from src.table.tables import TableUI

# Загрузка данных из БД в таблицу
def load_data_in_table(table_name, table_ui):
    data_card = DataBase.all_data_cards(table_name)
    TableUI.load_data_card(data_card, table_ui)

def load_data_config(ui_rate, ui_tables, ui_list):
    with open('src/initiation/data.config', 'r') as file:
        values = []

        for line in file:
            values.append(line.split()[-1])

        ui_rate.setValue(int(values[0]))
        ui_tables.setCurrentIndex(int(values[1]))
        ui_list.setCurrentIndex(int(values[2]))
