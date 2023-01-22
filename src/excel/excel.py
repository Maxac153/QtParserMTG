import pandas as pd


# Создание листа таблицы
def table_list(ui_table):
    number_card = []
    name = []
    name_set = []
    price_dollar = []
    price_ruble = []
    url = []

    rows = ui_table.rowCount()
    for row in range(rows):
        number_card.append(ui_table.item(row, 0).text())
        name.append(ui_table.item(row, 1).text())
        name_set.append(ui_table.item(row, 2).text())
        price_dollar.append(ui_table.item(row, 3).text())
        price_ruble.append(ui_table.item(row, 4).text())
        url.append(ui_table.item(row, 5).text())

    data_frame = pd.DataFrame(
        {
            "Количество карт": number_card,
            "Название": name,
            "Название сета": name_set,
            "Цена в рублях": price_ruble,
            "Цена в долларах": price_dollar,
            "Ссылка": url,
        }
    )
    return data_frame


# Сохранение данных в Excel
def save_to_excel(file_name, ui):
    data_frame1 = table_list(ui.TableStarCityGames)
    data_frame2 = table_list(ui.TableGoldFish)

    salary_shets = {"StarCityGames": data_frame1, "GoldFish": data_frame2}
    writer = pd.ExcelWriter(file_name, engine="xlsxwriter")

    for sheet_name in salary_shets.keys():
        salary_shets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)

    writer.close()


# Загрузка данных из таблицы
def load_data_from_excel(file_name, ui):
    cols = [0, 5]
    cards = pd.read_excel(file_name, usecols=cols)
    for card in cards.values:
        ui.NumberCards.append(str(card[0]))
        ui.LinkCards.append(card[1])
