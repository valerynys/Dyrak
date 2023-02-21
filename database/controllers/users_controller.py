import typing
from aiogram import types

from .table_controller import Controller
from ..models import User


class Users(Controller):
    @staticmethod
    def get_user(user_id: int) -> typing.Optional[User]:
        with Controller.conn as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `users` WHERE `user_id` = ?'
            c.execute(sql, (user_id, ))
            r = c.fetchone()
            if r:
                return User(**r)
            else:
                return None

    @staticmethod
    async def register_user(user: types.User, join_time: float) -> None:
        data = Users.get_user(user.id)
        if not data:
            with Controller.conn as conn:
                c = conn.cursor()
                sql = 'INSERT INTO `users` (user_id, username, join_time) VALUES (?, ?, ?)'
                c.execute(sql, (user.id, user.get_mention(), join_time))
                conn.commit()
