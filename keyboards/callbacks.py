from aiogram.utils.callback_data import CallbackData


class Callbacks:
    join_game_callback: CallbackData = CallbackData('join_game', 'chat_id')
    card_callback: CallbackData = CallbackData('card', 'card_id')
    turn_callback: CallbackData = CallbackData('turn', 'turn_type', 'card_id', 'chat_id')
    init_q_callback: CallbackData = CallbackData('players_count', 'chat_id', 'count', 'start')
