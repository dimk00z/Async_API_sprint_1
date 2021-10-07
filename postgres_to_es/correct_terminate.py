import logging
import signal
import sys
from datetime import datetime

from elasticsearch.client import Elasticsearch
from psycopg2.extensions import connection


class TerminateProtected:
    def __init__(self, pg_conn: connection, es: Elasticsearch) -> None:
        self.pg_conn = pg_conn
        self.es = es
        self.killed = False

    def _handler(self, signum, frame):
        logging.info("End etl_app at %s", datetime.now())
        self.pg_conn.close()
        logging.info("Postgres connection has been closed correctly")
        self.es.transport.close()
        logging.info("Elasticsearch connection has been closed correctly")
        self.killed = True

    def __enter__(self):
        self.old_sigint = signal.signal(signal.SIGINT, self._handler)
        self.old_sigterm = signal.signal(signal.SIGTERM, self._handler)

    def __exit__(self, type, value, traceback):
        if self.killed:
            sys.exit(0)
        signal.signal(signal.SIGINT, self.old_sigint)
        signal.signal(signal.SIGTERM, self.old_sigterm)
