import backoff
import psycopg2
from models import Person
from connections import backoff_hdlr
from extractors.base_extractor import BaseExtractor


class PersonsPostgresExtractor(BaseExtractor):
    def fetch_person_row(self, row: psycopg2.extras.DictRow) -> Person:
        person = Person(
            uuid=row["uuid"],
            full_name=row["full_name"],
            birth_date=row["birth_date"],
            updated_at=row["updated_at"],
        )
        return person

    @backoff.on_exception(
        backoff.expo,
        (psycopg2.Error, psycopg2.OperationalError),
        on_backoff=backoff_hdlr,
    )
    def extract_data(self) -> list[Person]:
        persons_query: str = " ".join(
            [
                "SELECT id as uuid, updated_at, full_name, birth_date",
                "FROM content.person",
                f"WHERE updated_at > '{self.last_state}'" if self.last_state else "",
                "ORDER BY updated_at;",
            ]
        )
        with self.pg_conn.cursor(name="person_cursor") as person_cursor:
            person_cursor.execute(persons_query)
            while data := person_cursor.fetchmany(self.cursor_limit):
                persons: list[Person] = []
                for person_row in data:
                    persons.append(self.fetch_person_row(row=person_row))
                yield persons
