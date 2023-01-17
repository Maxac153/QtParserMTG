from src.dataBase.data_base import DataBase
from src.table.tables import TablesUI

# Загрузка данных из БД в таблицу
def loding_data_in_table(name_table, ui_table):
    data = DataBase(())
    data_card = data.all_data_cards(name_table)

    table = TablesUI(data_card)
    table.load_data_card(ui_table)

def loding_data_config(ui_rate, ui_tables, ui_list):
    file = open('src/initiation/data.config', 'r')
    values = []

    for line in file:
        values.append(line.split()[-1])

    ui_rate.setText(values[0])
    ui_tables.setCurrentIndex(int(values[1]))
    ui_list.setCurrentIndex(int(values[2]))
    file.close()