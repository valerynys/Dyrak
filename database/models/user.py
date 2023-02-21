import typing
from pydantic.dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: typing.Optional[str]
    join_time: float
