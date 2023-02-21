import time

from aiogram import Bot, Dispatcher, executor, types

import database.controllers
from config import cfg
from game import Game
from keyboards import InlineKeyboards, Callbacks
from middlewares import ChatAdminMiddleware

bot = Bot(cfg.token, parse_mode='html', proxy='socks5://127.0.0.1:9150')
dp = Dispatcher(bot)


@dp.message_handler(types.ChatType.is_private, commands=["start"])
async def start_command_handler(msg: types.Message):
    await database.controllers.Users.register_user(msg.from_user, time.time())
    await msg.reply("Вы записаны в базу.\nПривет! Это бот для игры в Дурака. Чтобы играть, добавьте этого бота в ваш чат.")


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_chat_members_handler(msg: types.Message):
    me = await bot.get_me()
    if msg.new_chat_members[0].id == me.id:
        database.controllers.Chats.register_chat(msg.chat, time.time())
        await msg.reply("Бот добавлен! Для начала работы выдайте админ права")


@dp.message_handler(types.ChatType.is_group_or_super_group, commands=["startgame"])
async def start_game_command_handler(msg: types.Message):
    chat_id = msg.chat.id

    if await Game.init_queue(chat_id, msg.from_user.id):
        await msg.reply(
            'Выберите количество участников',
            reply_markup=InlineKeyboards.init_q(chat_id))
    else:
        await msg.reply('Набор уже идет')


@dp.callback_query_handler(Callbacks.init_q_callback.filter(start='false'))
async def players_count_callback_handler(q: types.CallbackQuery, callback_data: dict):
    chat_id = int(callback_data['chat_id'])

    game = Game(chat_id)
    players = await game.get_queue().get_players()
    if q.from_user.id != players[0]:
        await bot.answer_callback_query(q.id, 'Изменять количество участников может только создатель партии')
        return

    count = int(callback_data['count'])
    count = count + 1 if count < 4 else 2
    database.Chats.set_max_players(chat_id, count)
    await bot.edit_message_text('Выберите количество участников', chat_id,  q.message.message_id, reply_markup=InlineKeyboards.init_q(chat_id, count))


@dp.callback_query_handler(Callbacks.init_q_callback.filter(start='true'))
async def players_start_callback_handler(q: types.CallbackQuery, callback_data: dict):
    chat_id = int(callback_data['chat_id'])
    game = Game(chat_id)
    players = await game.get_queue().get_players()
    if q.from_user.id != players[0]:
        await bot.answer_callback_query(q.id, 'Начинать игру может только создатель партии')
        return

    await bot.edit_message_text(f'{q.from_user.get_mention()} создает игру!\nИгроков 1/{database.Chats.get_chat(chat_id).max_players}', chat_id, q.message.message_id, reply_markup=InlineKeyboards.join_game_keyboard(chat_id))


@dp.callback_query_handler(Callbacks.turn_callback.filter())
async def turn_callback_handler(q: types.CallbackQuery, callback_data: dict):
    chat_id = int(callback_data['chat_id'])
    game = Game(chat_id, bot)
    user_id, _ = await game.get_turn()

    if int(user_id) != q.from_user.id:
        await bot.answer_callback_query(q.id, 'Сейчас не ваш ход')
        return
    del callback_data['@']
    del callback_data['chat_id']
    await game.turn(**callback_data, q=q)


@dp.callback_query_handler(Callbacks.join_game_callback.filter())
async def join_game_callback_handler(q: types.CallbackQuery, callback_data: dict):
    user_id = q.from_user.id

    if not database.controllers.Users.get_user(user_id):
        await bot.answer_callback_query(q.id, 'Для начала напишите боту комманду /start')
        return

    chat_id = int(callback_data['chat_id'])
    chat = database.controllers.Chats.get_chat(chat_id)
    max_players = chat.max_players

    game = Game(chat_id)
    queue = game.get_queue()
    players = await queue.get_players()
    players_count = len(players)

    msg_id = q.message.message_id

    if user_id in await queue.get_players():
        await bot.answer_callback_query(q.id, 'Вы уже присоединились к игре')
        return

    await queue.add_player(user_id)
    if players_count + 1 == max_players:
        game.bot = bot
        await game.start()
        await bot.edit_message_text(f'Игра началась! Игроков: {max_players}', chat_id, msg_id)
    else:
        await bot.edit_message_text(
            f'<strong>{q.from_user.get_mention()}</strong> присоединился к игре\nИгроков присоединилось {players_count + 1}/{max_players}',
            chat_id, msg_id, reply_markup=InlineKeyboards.join_game_keyboard(chat_id))


if __name__ == "__main__":
    dp.middleware.setup(ChatAdminMiddleware())
    executor.start_polling(dp)
