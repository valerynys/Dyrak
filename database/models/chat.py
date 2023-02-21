from pydantic.dataclasses import dataclass


@dataclass
class Chat:
    chat_id: int
    max_players: int
    join_time: float
