import typing

from game.models import Card
from ..controller import Controller


class Deck:
    __deck_key: str = 'deck:{chat_id}'

    def __init__(self, chat_id: int) -> None:
        self.__deck_key = self.__deck_key.format(chat_id=chat_id)

    async def get_cards(self) -> typing.List[Card]:
        card_ids = await Controller.lrange(self.__deck_key, 36)
        del card_ids[0]
        return [Card(id=int(card_id)) for card_id in card_ids]

    async def set_cards(self, cards: typing.List[Card]) -> None:
        await Controller.delete(self.__deck_key)
        await Controller.rpush(self.__deck_key, 0, *[card.id for card in cards])

    async def clear(self):
        await Controller.delete(self.__deck_key)
