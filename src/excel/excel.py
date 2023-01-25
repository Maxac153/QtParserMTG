import pandas as pd

from ui.ui_imagedialog import MyWin


class ExcelHandler:
    number_card = []
    name = []
    name_set = []
    price_dollar = []
    price_ruble = []
    url = []
    ui: MyWin

    def __init__(self, ui: MyWin):
        self.ui = ui

    # Создание листа таблицы
    def table_list(self, ui_table):

        rows = ui_table.rowCount()
        for row in range(rows):
            self.number_card.append(ui_table.item(row, 0).text())
            self.name.append(ui_table.item(row, 1).text())
            self.name_set.append(ui_table.item(row, 2).text())
            self.price_dollar.append(ui_table.item(row, 3).text())
            self.price_ruble.append(ui_table.item(row, 4).text())
            self.url.append(ui_table.item(row, 5).text())

        data_frame = pd.DataFrame(
            {
                "Количество карт": self.number_card,
                "Название": self.name,
                "Название сета": self.name_set,
                "Цена в рублях": self.price_ruble,
                "Цена в долларах": self.price_dollar,
                "Ссылка": self.url,
            }
        )
        return data_frame

    # Сохранение данных в Excel
    def save_to_excel(self, file_name):
        data_frame1 = self.table_list(self.ui.TableStarCityGames)
        data_frame2 = self.table_list(self.ui.TableGoldFish)

        salary_shets = {"StarCityGames": data_frame1, "GoldFish": data_frame2}
        writer = pd.ExcelWriter(file_name, engine="xlsxwriter")

        for sheet_name in salary_shets.keys():
            salary_shets[sheet_name].to_excel(
                writer, sheet_name=sheet_name, index=False
            )

        writer.close()

    # Загрузка данных из таблицы
    def load_data_from_excel(self, file_name):
        cols = [0, 5]
        cards = pd.read_excel(file_name, usecols=cols)
        for card in cards.values:
            self.ui.NumberCards.append(str(card[0]))
            self.ui.LinkCards.append(card[1])
