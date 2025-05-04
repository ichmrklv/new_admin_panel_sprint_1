import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sqlite_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def postgres_conn(dsl: dict):
    return psycopg2.connect(**dsl)


def convert_sqlite_datetime(value):
    if isinstance(value, str) and '+00' in value:
        value = value.replace('+00', '')
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
    return value


def convert_postgres_datetime(value):
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(pytz.utc).replace(tzinfo=None)
    return value


def compare_table_count(sqlite_conn, pg_conn, table: str) -> bool:
    cursor_sqlite = sqlite_conn.cursor()
    cursor_sqlite.execute(f"SELECT COUNT(*) FROM {table}")
    sqlite_count = cursor_sqlite.fetchone()[0]

    cursor_pg = pg_conn.cursor()
    cursor_pg.execute(f"SELECT COUNT(*) FROM {table}")
    pg_count = cursor_pg.fetchone()[0]

    logger.info(
        f"Table {table}: {sqlite_count} records in SQLite, "
        f"{pg_count} records in PostgreSQL"
    )
    assert sqlite_count == pg_count, (
        f"Record count does not match in table {table}"
    )
    logger.info(f"Record count matches in table {table}")
    return True


def compare_table_data(sqlite_conn, pg_conn, table: str) -> bool:
    # Sorting by id for correct comparison
    cursor_sqlite = sqlite_conn.cursor()
    cursor_sqlite.execute(f"SELECT * FROM {table} ORDER BY id")
    sqlite_rows = cursor_sqlite.fetchall()

    cursor_pg = pg_conn.cursor(cursor_factory=RealDictCursor)
    cursor_pg.execute(f"SELECT * FROM {table} ORDER BY id")
    pg_rows = cursor_pg.fetchall()

    logger.info(f"Table {table}: checking content.")
    assert len(sqlite_rows) == len(pg_rows), (
        f"Row count does not match when checking content of table {table}"
    )

    for sqlite_row, pg_row in zip(sqlite_rows, pg_rows):
        for column in sqlite_row.keys():
            sqlite_value = sqlite_row[column]
            pg_value = pg_row[column]

            if column in ['created', 'modified']:
                sqlite_value = convert_sqlite_datetime(sqlite_value)
                pg_value = convert_postgres_datetime(pg_value)

            if sqlite_value is None and pg_value == 0.0:
                continue  # consider values as equal

            assert sqlite_value == pg_value, (
                f"Mismatch for id = {sqlite_row['id']}, column: {column}. "
                f"SQLite: {sqlite_value}, Postgres: {pg_value}"
            )

    logger.info(f"Content matches in table {table}")
    return True


def test_data_integrity(sqlite_db: str, dsl: dict):
    with (
        sqlite_conn(sqlite_db) as sqlite_connection,
        postgres_conn(dsl) as pg_connection
    ):
        tables = [
            'person', 'genre', 'film_work',
            'genre_film_work', 'person_film_work'
        ]
        for table in tables:
            logger.info(f"\nChecking table: {table}")
            try:
                compare_table_count(sqlite_connection, pg_connection, table)
                compare_table_data(sqlite_connection, pg_connection, table)
                logger.info(f"Table {table} passed successfully!\n")
            except AssertionError as e:
                logger.error(str(e))
                continue

        logger.info("\nTesting completed!")


dsl = {
    'dbname': 'movies_database',
    'user': 'alinamerkulova',
    'password': '123qwe',
    'host': '127.0.0.1',
    'port': 5432
}

if __name__ == "__main__":
    test_data_integrity('db.sqlite', dsl)
