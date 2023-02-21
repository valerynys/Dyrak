import typing
from aiogram import types

from .table_controller import Controller
from ..models import Chat


class Chats(Controller):
    @staticmethod
    def get_chat(chat_id: int) -> Chat:
        with Controller.conn as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `chats` WHERE `chat_id` = ?'
            c.execute(sql, (chat_id,))
            r = c.fetchone()
            if r:
                return Chat(**r)
            else:
                return None

    @staticmethod
    def register_chat(chat: types.Chat, join_time: float) -> None:
        data = Chats.get_chat(chat.id)
        if not data:
            with Controller.conn as conn:
                c = conn.cursor()
                sql = 'INSERT INTO `chats` (chat_id, max_players, join_time) VALUES (?, ?, ?)'
                c.execute(sql, (chat.id, 4, join_time))
                conn.commit()

    @staticmethod
    def set_max_players(chat_id: int, max_players: int):
        with Controller.conn as conn:
            c = conn.cursor()
            sql = 'UPDATE `chats` SET max_players = ? WHERE chat_id = ?'
            c.execute(sql, (max_players, chat_id))
            conn.commit()
