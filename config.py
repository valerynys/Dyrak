from pydantic.dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class Config:
    token: str = "980190998:AAGGLHLg8-mrR9TBNGjQ9DCAJUs0Uqdbqm0"
    db_name: Path = Path(__file__).parent / "db.db"
    cache_tuple: tuple = ("localhost", 6379)  # (os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'))


cfg = Config()
