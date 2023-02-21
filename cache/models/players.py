import typing

from ..controller import Controller


class Players:
    __players_key: str
    __player_message_key: str

    def __init__(self, chat_id: int):
        self.__players_key = f'players:{chat_id}'
        self.__player_message_key = f'player:message:{chat_id}'

    async def get_players(self) -> typing.List[int]:
        return [int(player) for player in await Controller.lrange(self.__players_key, 4)]

    async def add_player(self, user_id: int) -> None:
        await Controller.lpush(self.__players_key, user_id)

    async def players_exist(self) -> bool:
        return await Controller.exists(self.__players_key)

    async def delete_player(self, user_id: int) -> None:
        await Controller.lrem(self.__players_key, user_id)

    async def get_player_message(self, user_id: int) -> int:
        return int(await Controller.get(f'{self.__player_message_key}:{user_id}'))

    async def set_player_message(self, user_id: int, message_id: int) -> None:
        await Controller.set(f'{self.__player_message_key}:{user_id}', message_id)

    async def clear(self):
        await Controller.delete(self.__players_key)
