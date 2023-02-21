from ..connection import Connection
from config import Config
import typing


class Controller:
    __conn: Connection = Connection(Config.cache_tuple)
    @staticmethod
    async def get(key: str) -> str:
        async with Controller.__conn as conn:
            return await conn.get(key)

    @staticmethod
    async def set(key: str, value) -> None:
        async with Controller.__conn as conn:
            await conn.set(key, value)

    @staticmethod
    async def delete(key: str) -> None:
        async with Controller.__conn as conn:
            await conn.delete(key)

    @staticmethod
    async def lrange(key: str, stop: int) -> typing.List[str]:
        async with Controller.__conn as conn:
            return await conn.lrange(key, 0, stop)

    @staticmethod
    async def lpush(key: str, *values) -> None:
        async with Controller.__conn as conn:
            await conn.lpush(key, *values)

    @staticmethod
    async def rpush(key: str, *values) -> None:
        async with Controller.__conn as conn:
            await conn.rpush(key, *values)

    @staticmethod
    async def lrem(key: str, value) -> None:
        async with Controller.__conn as conn:
            await conn.lrem(key, 1, value)

    @staticmethod
    async def hmget(key: str, *fields) -> typing.Tuple[str]:
        async with Controller.__conn as conn:
            return await conn.hmget(key, *fields)

    @staticmethod
    async def hmset_dict(key: str, pairs: dict) -> None:
        async with Controller.__conn as conn:
            await conn.hmset_dict(key, pairs)

    @staticmethod
    async def exists(key: str) -> bool:
        async with Controller.__conn as conn:
            return await conn.exists(key)
