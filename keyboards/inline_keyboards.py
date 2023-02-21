import typing

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .callbacks import Callbacks
from game.models import Card


class InlineKeyboards:
    @staticmethod
    def __create_inline_keyboard(buttons: typing.List[InlineKeyboardButton] = None,
                                 rows: typing.List[typing.List[InlineKeyboardButton]] = None,
                                 width: int = 1) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(row_width=width)
        if buttons:
            [keyboard.add(button) for button in buttons]
        if rows:
            [keyboard.row(*row) for row in rows]
        return keyboard

    @staticmethod
    def join_game_keyboard(chat_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboards.__create_inline_keyboard(
            [InlineKeyboardButton("Присоединиться", callback_data=Callbacks.join_game_callback.new(chat_id=chat_id))])

    @staticmethod
    def cards_keyboard(chat_id: int, cards: typing.List[Card]):
        return InlineKeyboards.__create_inline_keyboard([InlineKeyboardButton(str(card),
                                                                              callback_data=Callbacks.turn_callback.new(
                                                                                  turn_type='card', card_id=card.id,
                                                                                  chat_id=chat_id)) for card in cards],
                                                        width=2)

    @staticmethod
    def pass_struggle_keyboard(keyboard: InlineKeyboardMarkup, chat_id: int):
        return keyboard.add(InlineKeyboardButton('Взять карты',
                                                 callback_data=Callbacks.turn_callback.new(turn_type='pass_struggle',
                                                                                           card_id='0',
                                                                                           chat_id=chat_id)))

    @staticmethod
    def pass_toss_keyboard(keyboard: InlineKeyboardMarkup, chat_id: int):
        return keyboard.add(InlineKeyboardButton('Не подкидывать',
                                                 callback_data=Callbacks.turn_callback.new(turn_type='pass_toss',
                                                                                           card_id='0',
                                                                                           chat_id=chat_id)))

    @staticmethod
    def init_q(chat_id: int, count=2):
        return InlineKeyboards.__create_inline_keyboard([InlineKeyboardButton(f'{count}', callback_data=Callbacks.init_q_callback.new(count=count, chat_id=chat_id, start='false')), InlineKeyboardButton('Начать игру', callback_data=Callbacks.init_q_callback.new(count='0', chat_id=chat_id, start='true'))])
