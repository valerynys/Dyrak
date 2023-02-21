import typing
import cache.models


class Queue:
    __players: cache.models.Players

    @staticmethod
    async def create(chat_id: int, user_id: int) -> bool:
        players = cache.models.Players(chat_id)
        if await players.players_exist():
            return False
        await players.add_player(user_id)
        return True

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.__players = cache.models.Players(chat_id)

    async def get_players(self) -> typing.List[int]:
        return await self.__players.get_players()

    async def add_player(self, user_id: int):
        await self.__players.add_player(user_id)
