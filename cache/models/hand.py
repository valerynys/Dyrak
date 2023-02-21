import typing

from game.models import Card
from ..controller import Controller


class Hand:
    __hand_key: str

    def __init__(self, chat_id: int):
        self.__hand_key = f'hand:{chat_id}'

    async def get_cards(self, user_id: int) -> typing.List[Card]:
        return [Card(id=int(card_id)) for card_id in await Controller.lrange(f'{self.__hand_key}:{user_id}', 35)]

    async def add_cards(self, user_id: int, cards: typing.List[Card]) -> None:
        await Controller.lpush(f'{self.__hand_key}:{user_id}', *[card.id for card in cards])

    async def delete_card(self, user_id: int, card: Card) -> None:
        await Controller.lrem(f'{self.__hand_key}:{user_id}', card.id)

    async def clear(self, user_id):
        await Controller.delete(f'{self.__hand_key}:{user_id}')
