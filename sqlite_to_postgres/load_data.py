import os
import sqlite3
from datetime import datetime
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List
from psycopg2.extras import RealDictCursor
import psycopg2
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Person:
    id: str
    full_name: str
    created: datetime
    modified: datetime


@dataclass
class Genre:
    id: str
    name: str
    description: str
    created: datetime
    modified: datetime


@dataclass
class FilmWork:
    id: str
    title: str
    description: str
    creation_date: str
    file_path: str
    rating: float
    type: str
    created: datetime
    modified: datetime


@contextmanager
def sqlite_conn_context(db_path: str):
    """Context manager for SQLite connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def postgres_conn_context(dsl: dict):
    """Context manager for PostgreSQL connection"""
    conn = psycopg2.connect(**dsl, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


class SQLiteLoader:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def load_data(self, table: str, batch_size: int = 1000):
        """Loads data from SQLite with batch selection"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_rows = cursor.fetchone()[0]
            logger.info(f"Table {table} contains {total_rows} records.")
            # Loading data in batches
            offset = 0
            while offset < total_rows:
                cursor.execute(
                    f"SELECT * FROM {table} "
                    f"LIMIT {batch_size} OFFSET {offset}"
                    )
                yield cursor.fetchall()
                offset += batch_size
        except Exception as e:
            logger.error(f"Error reading from table {table}: {e}")


class PostgresSaver:
    def __init__(self, conn: psycopg2.extensions.connection):
        self.conn = conn

    def save_persons(self, data: List[sqlite3.Row]):
        cursor = self.conn.cursor()
        for row in data:
            try:
                cursor.execute("""
                    INSERT INTO person (id, full_name, created, modified)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row['id'],
                    row['full_name'],
                    row['created'] or datetime.now(),
                    row['modified'] or datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Error inserting person {row['id']}: {e}")
        self.conn.commit()

    def save_genres(self, data: List[sqlite3.Row]):
        cursor = self.conn.cursor()
        for row in data:
            try:
                cursor.execute("""
                    INSERT INTO genre (
                               id, name, description, created, modified
                               )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row['id'], row['name'], row['description'],
                    row['created'] or datetime.now(),
                    row['modified'] or datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Error inserting genre {row['id']}: {e}")
        self.conn.commit()

    def save_film_works(self, data: List[sqlite3.Row]):
        cursor = self.conn.cursor()
        for row in data:
            rating = row['rating'] if row['rating'] is not None else 0.0
            try:
                cursor.execute("""
                    INSERT INTO film_work (
                        id, title, description, creation_date, file_path,
                        rating, type, created, modified
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row['id'], row['title'], row['description'],
                    row['creation_date'], row['file_path'],
                    rating, row['type'],
                    row['created'] or datetime.now(),
                    row['modified'] or datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Error inserting film_work {row['id']}: {e}")
        self.conn.commit()

    def save_person_film_work(self, data: List[sqlite3.Row]):
        cursor = self.conn.cursor()
        for row in data:
            created = (
                row['created'] if row['created'] is not None
                else datetime.now()
                )
            try:
                cursor.execute("""
                    INSERT INTO person_film_work (
                        id, role, created, film_work_id, person_id
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row['id'], row['role'], created,
                    row['film_work_id'], row['person_id']
                    ))
            except Exception as e:
                logger.warning(
                    f"Error inserting person_film_work {row['id']}: {e}"
                )
        self.conn.commit()

    def save_genre_film_work(self, data: List[sqlite3.Row]):
        cursor = self.conn.cursor()
        for row in data:
            if row['created'] is not None:
                created = row['created']
            else:
                created = datetime.now()
            try:
                cursor.execute("""
                    INSERT INTO genre_film_work (
                        id, created, film_work_id, genre_id
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    row['id'], created, row['film_work_id'], row['genre_id']
                ))
            except Exception as e:
                logger.warning(
                    f"Error inserting genre_film_work {row['id']}: {e}"
                )
        self.conn.commit()


def load_from_sqlite(
    sqlite_conn: sqlite3.Connection,
    pg_conn: psycopg2.extensions.connection
):
    """Main method to load data from SQLite to Postgres"""
    loader = SQLiteLoader(sqlite_conn)
    saver = PostgresSaver(pg_conn)

    for persons_batch in loader.load_data('person', batch_size=1000):
        logger.info(f"Loaded {len(persons_batch)} persons from SQLite.")
        saver.save_persons(persons_batch)

    for genres_batch in loader.load_data('genre', batch_size=1000):
        logger.info(f"Loaded {len(genres_batch)} genres from SQLite.")
        saver.save_genres(genres_batch)

    for film_works_batch in loader.load_data('film_work', batch_size=1000):
        logger.info(f"Loaded {len(film_works_batch)} film works from SQLite.")
        saver.save_film_works(film_works_batch)

    for person_film_work_batch in loader.load_data(
        'person_film_work', batch_size=1000
    ):
        logger.info(
            f"Loaded {len(person_film_work_batch)} "
            "person_film_work records from SQLite."
        )
        saver.save_person_film_work(person_film_work_batch)

    for genre_film_work_batch in loader.load_data(
        'genre_film_work', batch_size=1000
    ):
        logger.info(
            f"Loaded {len(genre_film_work_batch)} "
            "genre_film_work records from SQLite."
        )
        saver.save_genre_film_work(genre_film_work_batch)


if __name__ == '__main__':
    load_dotenv()

    dsl = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
    }

    with (
        sqlite_conn_context('db.sqlite') as sqlite_conn,
        postgres_conn_context(dsl) as pg_conn
    ):
        load_from_sqlite(sqlite_conn, pg_conn)
