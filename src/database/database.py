import sqlite3 as sq

class DataBase:
    @staticmethod
    def add_card(data_card, table_name: str = '') -> None:
        with sq.connect('src/database/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                INSERT INTO {table_name}
                VALUES(?, ?, ?, ?, ?, ?) 
            """,
                data_card,
            )

    @staticmethod
    def remove_card(data_card, table_name: str = '') -> None:
        with sq.connect('src/database/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                DELETE
                FROM {table_name}
                WHERE url = "{data_card}"
            """
            )

    @staticmethod
    def remove_cards(table_name: str = '') -> None:
        with sq.connect('src/database/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                DELETE
                FROM {table_name}
            """
            )

    @staticmethod
    def update_price_card(data_card, table_name: str = '') -> None:
        with sq.connect('src/database/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                UPDATE {table_name}
                SET price_dollar = "{data_card[3]}", price_ruble = "{data_card[4]}"
                WHERE url = "{data_card[5]}"
            """
            )

    @staticmethod
    def recalculation(price_ruble, table_name: str = '', link: str = '') -> None:
        with sq.connect('src/database/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                UPDATE {table_name}
                SET price_ruble = "{price_ruble}"
                WHERE url = "{link}"
            """
            )
    @staticmethod
    def all_data_cards(table_name: str = '') -> list[tuple[str, str, str, str, str, str]]:
        with sq.connect('src/database/cards.db') as con:
            cur = con.cursor()
            cur.execute(
                f"""
                SELECT *
                FROM {table_name}
            """
            )
            data_cards = cur.fetchall()
        return data_cards
