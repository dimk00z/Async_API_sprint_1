from dataclasses import dataclass

import psycopg2


class BaseExtractor:
    def __init__(
        self,
        pg_conn: psycopg2.extensions.connection,
        last_state: str = "",
        cursor_limit: int = 200,
    ) -> None:
        self.pg_conn = pg_conn
        self.last_state: str = last_state
        self.cursor_limit = cursor_limit

    def extract_data(self) -> list[dataclass]:
        pass
