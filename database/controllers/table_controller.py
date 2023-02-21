from pathlib import Path

from ..connection import Connection
from config import Config


class Controller:
    db_name: Path = Config.db_name
    conn: Connection = Connection(Config.db_name)
