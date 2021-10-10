import logging
from typing import List

import backoff
import psycopg2
from models import Genre
from connections import backoff_hdlr


class GenresPostgresExtractor:
    def __init__(
        self,
        pg_conn: psycopg2.extensions.connection,
        last_state: str = "",
        cursor_limit: int = 200,
    ) -> None:
        self.pg_conn = pg_conn
        self.last_state: str = last_state
        self.cursor_limit = cursor_limit

    def fetch_genre_row(self, row: psycopg2.extras.DictRow) -> Genre:
        genre = Genre(uuid=row["uuid"], name=row["name"], updated_at=row["updated_at"])
        return genre

    @backoff.on_exception(
        backoff.expo,
        (psycopg2.Error, psycopg2.OperationalError),
        on_backoff=backoff_hdlr,
    )
    def extract_genres(self) -> List[Genre]:
        genres_query: str = " ".join(
            [
                "SELECT id as uuid, updated_at, name",
                "FROM content.genre",
                f"WHERE updated_at > '{self.last_state}'" if self.last_state else "",
                "ORDER BY updated_at;",
            ]
        )
        with self.pg_conn.cursor(name="genres_id_cursor") as genres_id_cursor:
            genres_id_cursor.execute(genres_query)
            while data := genres_id_cursor.fetchmany(self.cursor_limit):
                genres: List[Genre] = []
                for genre_row in data:
                    genres.append(self.fetch_genre_row(row=genre_row))
                yield genres
