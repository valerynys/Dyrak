import sqlite3
from pathlib import Path


class Connection:
    db_name: Path
    conn: sqlite3.Connection

    def __init__(self, db_name: Path):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise
