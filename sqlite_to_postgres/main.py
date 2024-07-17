import sqlite3
from contextlib import contextmanager
import logging

loger=logging.basicConfig()



@contextmanager
def connection(db_path):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    try:
        yield conn
    finally:
        print("eee boi ")Q
        conn.close()

db_path="db.sqlite"

with connection(db_path) as conn:
    print(conn.cursor().execute("""SELECT * FROM film_work ;""").fetchall())


