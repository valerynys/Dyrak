import aioredis


class Connection:
    cache_tuple: tuple
    conn: aioredis.Redis

    def __init__(self, connection_tuple: tuple):
        self.cache_tuple = connection_tuple

    async def __aenter__(self):
        self.conn = await aioredis.create_redis_pool(self.cache_tuple)  # , db=15, password='997f1ab30256cce09aba331111f87985cbe3ec390a7ad495fa6379f4fcb73525')
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        await self.conn.wait_closed()
        if exc_val:
            raise
