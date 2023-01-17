import sqlite3 as sq

class DataBase:
    def __init__(self, data_card = ()):
        self.data_card = data_card

    def add_card(self, name_table):
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(f'''
                INSERT INTO {name_table}
                VALUES(?, ?, ?, ?, ?, ?) 
            ''', self.data_card)

    def remove_card(self, name_table):
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(f'''
                DELETE
                FROM {name_table}
                WHERE url = "{self.data_card[0]}"
            ''')

    def remove_cards(self, name_table):
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(f'''
                DELETE
                FROM {name_table}
            ''')

    def update_price_card(self, name_table, url):
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(f'''
                UPDATE {name_table}
                SET price_dollar = "{self.data_card[0]}", price_ruble = "{self.data_card[1]}"
                WHERE url = "{url}"
            ''')

    def recalculation(self, name_table, url):
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(f'''
                UPDATE {name_table}
                SET price_ruble = "{self.data_card}"
                WHERE url = "{url}"
            ''')

    def all_data_cards(self, name_table):
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(f'''
                SELECT *
                FROM {name_table}
            ''')
            rows = cur.fetchall()
        return rows