import logging
import os
import sqlite3
import uuid
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

import psycopg
from dotenv import load_dotenv
from psycopg import ClientCursor
from psycopg import connection as _connection
from psycopg.rows import dict_row
from psycopg.extras import execute_values

load_dotenv()

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
from classes import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork

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
            batch_data = []
            for row in data:
                # Заменяем NULL на пустую строку для поля file_path
                if table_name == 'film_work' and row.get('file_path') is None:
                    row['file_path'] = ''

                batch_data.append(row)
                if len(batch_data) >= 100:
                    self._insert_batch(cursor, table_name, batch_data)
                    batch_data.clear()
            if batch_data:
                self._insert_batch(cursor, table_name, batch_data)
            self.connection.commit()

    def _insert_batch(self, cursor, table_name, batch_data):
        if not batch_data:
            return

        columns = ', '.join(batch_data[0].keys())
        values_template = ', '.join(['%s'] * len(batch_data[0]))
        sql = f"""
        INSERT INTO content.{table_name} ({columns}) VALUES %s
        ON CONFLICT (id) DO NOTHING
        """
        execute_values(cursor, sql, [tuple(row.values()) for row in batch_data])


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
    dsl = {'dbname': os.environ.get("DB_NAME"), 'user': os.environ.get("USER"), 'password': os.environ.get("PASSWORD"), 'host': os.environ.get("HOST"), 'port': os.environ.get("PORT")}
    try:
        with closing(sqlite3.connect('db.sqlite')) as sqlite_conn, closing(psycopg.connect(
            **dsl, row_factory=dict_row, cursor_factory=ClientCursor
        )) as pg_conn:
            logging.info("Начало переноса данных из SQLite в PostgreSQL")
            load_from_sqlite(sqlite_conn, pg_conn)
            logging.info("Перенос данных из SQLite в PostgreSQL завершен")
    except Exception as e:
        logging.critical(f"Критическая ошибка при подключении к базам данных: {e}", exc_info=True)
