import sqlite3 as sq

class DataBase:
    def __init__(self, data_card=()):
        self.data_card = data_card

    def add_card(self, table_name: str = '') -> None:
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                INSERT INTO {table_name}
                VALUES(?, ?, ?, ?, ?, ?) 
            """,
                self.data_card,
            )

    def remove_card(self, table_name: str = '') -> None:
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                DELETE
                FROM {table_name}
                WHERE url = "{self.data_card[0]}"
            """
            )

    def remove_cards(self, table_name: str = '') -> None:
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                DELETE
                FROM {table_name}
            """
            )

    def update_price_card(self, table_name: str = '', url: str = '') -> None:
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                UPDATE {table_name}
                SET price_dollar = "{self.data_card[0]}", price_ruble = "{self.data_card[1]}"
                WHERE url = "{url}"
            """
            )

    def recalculation(self, table_name: str = '', url: str = '') -> None:
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                UPDATE {table_name}
                SET price_ruble = "{self.data_card}"
                WHERE url = "{url}"
            """
            )

    def all_data_cards(self, table_name: str = '') -> None:
        with sq.connect('src/dataBase/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                SELECT *
                FROM {table_name}
            """
            )
            rows = cur.fetchall()
        return rows
