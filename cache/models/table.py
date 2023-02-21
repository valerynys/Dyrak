import typing

from game.models import Card
from ..controller import Controller


class Table:
    __table_key: str

    def __init__(self, chat_id: int):
        self.__table_key = f'table:{chat_id}'

    async def get_cards(self) -> typing.List[Card]:
        return [Card(id=int(card_id)) for card_id in await Controller.lrange(self.__table_key, 35)]

    async def add_card(self, card: Card) -> None:
        await Controller.lpush(self.__table_key, card.id)

    async def clear(self) -> None:
        await Controller.delete(self.__table_key)
