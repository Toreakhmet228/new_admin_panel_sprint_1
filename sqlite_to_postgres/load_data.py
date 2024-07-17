import sqlite3
import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row
from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Union
import logging
from contextlib import contextmanager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_transfer.log"),
        logging.StreamHandler()
    ]
)

# Импортируйте классы данных из вашего модуля
from classes import Genre, GenreFilmWork, FilmWork, PersonFilmWork, Person

CLASSES_FOR_BD = {
    "film_work": FilmWork,
    "genre": Genre,
    "person": Person,
    "genre_film_work": GenreFilmWork,
    "person_film_work": PersonFilmWork,
}

class SQLiteLoader:
    FETCH_SIZE = 100

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def load_movies(self, table):
        cursor = self.connection.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute(f"SELECT * FROM {table}")
        while rows := cursor.fetchmany(self.FETCH_SIZE):
            for row in rows:
                yield dict(row)


class PostgresSaver:
    def __init__(self, connection: _connection):
        self.connection = connection

    def save_all_data(self, data, table_name):
        with self.connection.cursor() as cursor:
            for row in data:
                # Заменяем NULL на пустую строку для поля file_path
                if table_name == 'film_work' and row.get('file_path') is None:
                    row['file_path'] = ''

                placeholders = ', '.join(['%s'] * len(row))
                columns = ', '.join(row.keys())
                sql = f"""
                INSERT INTO content.{table_name} ({columns}) VALUES ({placeholders})
                ON CONFLICT (id) DO NOTHING
                """
                cursor.execute(sql, tuple(row.values()))
            self.connection.commit()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    for table_name, bd_class in CLASSES_FOR_BD.items():
        try:
            logging.info(f"Начало загрузки данных из таблицы {table_name}")
            data = sqlite_loader.load_movies(table_name)
            postgres_saver.save_all_data(data, table_name)
            logging.info(f"Загрузка данных из таблицы {table_name} завершена")
        except Exception as e:
            logging.error(f"Ошибка при загрузке данных из таблицы {table_name}: {e}", exc_info=True)


if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    try:
        with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
            **dsl, row_factory=dict_row, cursor_factory=ClientCursor
        ) as pg_conn:
            logging.info("Начало переноса данных из SQLite в PostgreSQL")
            load_from_sqlite(sqlite_conn, pg_conn)
            logging.info("Перенос данных из SQLite в PostgreSQL завершен")
    except Exception as e:
        logging.critical(f"Критическая ошибка при подключении к базам данных: {e}", exc_info=True)
