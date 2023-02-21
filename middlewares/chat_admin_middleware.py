from aiogram.dispatcher import Dispatcher
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler


class ChatAdminMiddleware(BaseMiddleware):
    def __init__(self):
        super(ChatAdminMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        chat = message.chat
        if (chat.type == types.chat.ChatType.GROUP or chat.type == types.chat.ChatType.SUPER_GROUP) and len(message.new_chat_members) == 0:
            dp = Dispatcher.get_current()
            me = await dp.bot.get_me()
            if me.id not in [admin.user.id for admin in await chat.get_administrators()]:
                await message.reply("Бот должен иметь права администратора")
                raise CancelHandler()
