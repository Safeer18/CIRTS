import pymysql
from pymysql.cursors import DictCursor
from dotenv import dotenv_values

config = dotenv_values(".env")

class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=config.get("DB_HOST", "localhost"),
                user=config.get("DB_USER"),
                password=config.get("DB_PASSWORD"),
                database=config.get("DB_NAME"),
                cursorclass=DictCursor,
                autocommit=True
            )
        except pymysql.MySQLError as e:
            raise RuntimeError(f"Database connection error: {e}")

    def close(self):
        if self.connection:
            self.connection.close()

    def fetch_one(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
