import typing

from game.models import Card
from ..controller import Controller


class State:
    __turn_key: str
    __trump_suit_key: str
    __struggle_key: str
    __struggled_key: str
    __next_toss_key: str
    __tossed_key: str

    def __init__(self, chat_id: int):
        self.__turn_key = f'turn:{chat_id}'
        self.__trump_suit_key = f'trump:suit:{chat_id}'
        self.__trump_card_key = f'trump:card:{chat_id}:'
        self.__struggle_key = f'struggle:{chat_id}'
        self.__struggled_key = f'struggled:{chat_id}'
        self.__next_toss_key = f'next_toss:{chat_id}'
        self.__tossed_key = f'tossed:{chat_id}'

    async def get_turn(self) -> typing.Tuple[int, str]:
        turn = await Controller.hmget(self.__turn_key, 'user_id', 'turn_type')
        return int(turn[0]), turn[1]

    async def set_turn(self, user_id: int, turn_type: str) -> None:
        await Controller.hmset_dict(self.__turn_key, {'user_id': str(user_id), 'turn_type': turn_type})

    async def get_struggle(self) -> int:
        return int(await Controller.get(self.__struggle_key))

    async def set_struggle(self, user_id: int) -> None:
        await Controller.set(self.__struggle_key, user_id)

    async def get_next_toss(self) -> int:
        return int(await Controller.get(self.__next_toss_key))

    async def set_next_toss(self, user_id: int) -> None:
        await Controller.set(self.__next_toss_key, user_id)

    async def get_tossed(self) -> typing.List[int]:
        return [int(user_id) for user_id in await Controller.lrange(self.__tossed_key, 4)]

    async def add_tossed(self, user_id: int) -> None:
        await Controller.lpush(self.__tossed_key, user_id)

    async def clear_tossed(self) -> None:
        await Controller.delete(self.__tossed_key)

    async def get_struggled(self) -> int:
        return int(await Controller.get(self.__struggled_key))

    async def set_struggled(self, value) -> None:
        await Controller.set(self.__struggled_key, value)

    async def get_trump_suit(self) -> int:
        return int(await Controller.get(self.__trump_suit_key))

    async def set_trump_suit(self, card: Card) -> None:
        await Controller.set(self.__trump_suit_key, card.suit_id)

    async def get_trump_card(self) -> Card:
        return Card(id=int(await Controller.get(self.__trump_card_key)))

    async def set_trump_card(self, card: Card) -> None:
        await Controller.set(self.__trump_card_key, card.id)
