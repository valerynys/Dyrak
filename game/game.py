import random
import time
import typing

from aiogram import Bot, types, exceptions

import cache.models
import database.controllers
from keyboards import InlineKeyboards
from .models import Card, Deck
from .queue import Queue


class Game:
    chat_id: int
    bot: Bot
    __deck: cache.models.Deck
    __hand: cache.models.Hand
    __players: cache.models.Players
    __state: cache.models.State
    __table: cache.models.Table

    def __init__(self, chat_id: int, bot: Bot = None):
        self.chat_id = chat_id
        self.__deck = cache.models.Deck(chat_id)
        self.__hand = cache.models.Hand(chat_id)
        self.__players = cache.models.Players(chat_id)
        self.__state = cache.models.State(chat_id)
        self.__table = cache.models.Table(chat_id)
        if bot:
            self.bot = bot

    @staticmethod
    async def init_queue(chat_id: int, user_id: int) -> bool:
        return await Queue.create(chat_id, user_id)

    def get_queue(self) -> Queue:
        return Queue(self.chat_id)

    async def _next_player(self, user_id: int, delta: int = 0) -> int:
        players = await self.__players.get_players()
        return players[(players.index(user_id) + 1 + delta) % len(players)]

    async def _set_next_toss(self) -> bool:
        cur_toss = await self.__state.get_next_toss()
        struggle = await self.__state.get_struggle()
        players = await self.__players.get_players()
        tossed_players = await self.__state.get_tossed()

        remain = list(set(players) - set(tossed_players))
        del remain[remain.index(struggle)]

        if len(remain) != 0:
            next_toss = remain[(remain.index(cur_toss) + 1) % len(remain)]
            await self.__state.set_next_toss(next_toss)
            return True
        return False

    async def get_turn(self) -> typing.Tuple[int, str]:
        return await self.__state.get_turn()

    async def start(self):
        queue = self.get_queue()
        deck = Deck(self.chat_id)
        trump_card = deck.get_trump_card()

        players = await queue.get_players()
        random.seed(int(str(self.chat_id) + str(int(time.time()))))
        rand_player = random.choice(players)
        struggle_player = await self._next_player(rand_player)

        for user_id in players:
            hand = deck.pop_cards(6)
            await self.__hand.add_cards(user_id, hand)

            text = f'Козырь - {str(trump_card)}'
            if user_id == rand_player:
                text = '<strong>Ваш ход</strong>\n\n' + text
            elif user_id == struggle_player:
                text = '<strong>Вы отбиваетесь</strong>\n\n' + text

            msg = await self.bot.send_message(user_id, text,
                                              reply_markup=InlineKeyboards.cards_keyboard(self.chat_id, hand))
            await self.__players.set_player_message(user_id, msg.message_id)

        await self.__state.set_trump_suit(trump_card)
        await self.__state.set_trump_card(trump_card)
        await self.__state.set_turn(rand_player, 'move')
        await self.__state.set_struggle(struggle_player)
        await self.__state.set_struggled(1)
        await self.__state.set_next_toss(rand_player)

        await self.__deck.set_cards(deck.cards)

    async def end(self):
        players = await self.__players.get_players()
        await self.__hand.clear(players[0])
        await self.__players.delete_player(players[0])
        await self.__deck.clear()
        await self.__table.clear()
        await self.bot.send_message(self.chat_id, f'Игра закончена.\nПроигравший - {database.Users.get_user(players[0]).username}')
        await self.bot.edit_message_text('Вы проиграли', players[0], await self.__players.get_player_message(players[0]))

    async def edit_messages(self, trigger_player: int, trigger_text: str, trigger_keyboard_function, additional_condition: bool = True) -> None:
        players = await self.__players.get_players()
        trump_card = await self.__state.get_trump_card()
        for player in players:
            text = f'Козырь - {str(trump_card)}\nКарт в колоде - {len(await self.__deck.get_cards())}'
            keyboard = InlineKeyboards.cards_keyboard(self.chat_id, await self.__hand.get_cards(player))
            message_id = await self.__players.get_player_message(player)
            if player == trigger_player and additional_condition:
                keyboard = trigger_keyboard_function(keyboard, self.chat_id)
                text = trigger_text + text
            try:
                await self.bot.edit_message_text(text, player, message_id, reply_markup=keyboard)
            except exceptions.MessageNotModified:
                pass

    async def turn(self, turn_type: str, card_id: str, q: types.CallbackQuery) -> None:
        user_id, turn = await self.get_turn()
        user_id = int(user_id)
        card_id = int(card_id)
        username = database.controllers.Users.get_user(user_id).username
        trump_suit = await self.__state.get_trump_suit()
        trump_card = await self.__state.get_trump_card()
        card = Card(id=card_id) if card_id else None

        if turn_type == 'card':
            if turn == b'move':
                struggle = await self.__state.get_struggle()
                await self.__table.add_card(Card(id=card_id))
                await self.__hand.delete_card(user_id, card)

                await self.edit_messages(struggle, f'Отбейте {str(card)}\n\n', InlineKeyboards.pass_struggle_keyboard)

                struggle_username = database.controllers.Users.get_user(struggle).username
                await self.bot.send_message(self.chat_id,
                                            f'Игрок @{username} сходил {str(Card(id=card_id))}.\nИгрок {struggle_username} отбивается')

                await self.__state.set_turn(struggle, 'struggle')
            elif turn == b'struggle':
                table = await self.__table.get_cards()
                struggle_card = table[0]
                if card.beat(struggle_card, trump_suit):
                    table.append(card)

                    await self.__table.add_card(card)
                    await self.__hand.delete_card(user_id, card)

                    hand = await self.__hand.get_cards(user_id)
                    if len(hand) == 0:
                        await self.bot.send_message(self.chat_id,
                                                    f'Игрок {username} отбивается {str(card)}. Ход окончен.')
                        await self.end_turn()
                        return

                    toss = await self.__state.get_next_toss()

                    await self.edit_messages(toss, 'Подкинуть? Карты на столе\n' + ' '.join([str(i) for i in table]) + '\n\n', InlineKeyboards.pass_toss_keyboard)

                    toss_username = database.controllers.Users.get_user(toss).username
                    await self.bot.send_message(self.chat_id,
                                                f'Игрок @{username} отбил {str(card)}.\nИгрок @{toss_username} подкидывает')

                    await self.__state.set_turn(toss, 'toss')
                else:
                    await self.bot.answer_callback_query(q.id, 'Невозможно отбить этой картой')
            elif turn == b'toss':
                table = await self.__table.get_cards()
                if Card(id=card_id).name_id in [i.name_id for i in table]:
                    await self.__table.add_card(card)
                    await self.__hand.delete_card(user_id, card)

                    struggle = await self.__state.get_struggle()
                    struggled = await self.__state.get_struggled()

                    await self.edit_messages(struggle, f'Отбейте{str(Card(id=card_id))}\n\nКарты на столе\n' + ' '.join([str(i) for i in table]) + '\n\n', InlineKeyboards.pass_struggle_keyboard, struggled == 1)

                    text = f'Игрок @{username} подкинул {str(Card(id=card_id))}'

                    if struggled == 1:
                        struggle_username = database.controllers.Users.get_user(struggle).username
                        text += f'\n@{struggle_username} отбивается'
                        await self.__state.clear_tossed()
                        await self.__state.set_turn(struggle, 'struggle')
                    else:
                        next_toss = await self.__state.get_next_toss()
                        message_id = await self.__players.get_player_message(next_toss)
                        try:
                            table.append(card)
                            cards = await self.__hand.get_cards(next_toss)
                            keyboard = InlineKeyboards.cards_keyboard(self.chat_id, cards)
                            await self.bot.edit_message_text(
                                'Подкинуть? Карты на столе\n' + ' '.join([str(i) for i in table]) + '\n\n', next_toss,
                                message_id, reply_markup=InlineKeyboards.pass_toss_keyboard(keyboard, self.chat_id))
                        except exceptions.MessageNotModified:
                            pass
                        await self.__state.set_turn(next_toss, 'toss')

                    await self.bot.send_message(self.chat_id, text)

                else:
                    await self.bot.answer_callback_query(q.id, 'Невозможно подкинуть эту карту')
        elif turn_type == 'pass_toss':
            username = database.controllers.Users.get_user(user_id).username
            await self.bot.send_message(self.chat_id, f'Игрок @{username} решил не подкидывать')
            cur_toss = await self.__state.get_next_toss()
            set_next_toss = await self._set_next_toss()
            if cur_toss == await self.__state.get_next_toss():
                await self.end_turn()
                return
            await self.__state.add_tossed(user_id)
            if set_next_toss:
                toss = await self.__state.get_next_toss()
                table = await self.__table.get_cards()

                await self.edit_messages(toss, f'Подкинуть? Карты на столе\n' + ' '.join([str(i) for i in table]) + '\n\n', InlineKeyboards.pass_toss_keyboard)

                await self.__state.set_turn(toss, 'toss')
            else:
                await self.end_turn()

        elif turn_type == 'pass_struggle':
            await self.__state.set_struggled(0)

            toss = await self.__state.get_next_toss()
            table = await self.__table.get_cards()

            await self.edit_messages(toss, f'Подкинуть? Карты на столе\n' + ' '.join([str(i) for i in table]) + '\n\n', InlineKeyboards.pass_toss_keyboard)
            await self.bot.send_message(self.chat_id, f'Игрок @{username} решил взять карты')
            await self.__state.set_turn(toss, 'toss')

    async def end_turn(self) -> None:
        struggle = await self.__state.get_struggle()
        struggled = await self.__state.get_struggled()
        table = await self.__table.get_cards()
        deck = await self.__deck.get_cards()
        players = [*[player for player in await self.__players.get_players() if player != struggle], struggle]
        players_len = len(players)
        if struggled == 0:
            await self.__hand.add_cards(struggle, table)
            next_struggle = await self._next_player(struggle, 1)
            next_move = await self._next_player(struggle)
        else:
            next_struggle = await self._next_player(struggle)
            next_move = struggle

        for player in players:
            hand = await self.__hand.get_cards(player)
            hand_len = len(hand)
            if len(deck) > 0:
                if hand_len < 6:
                    add_len = 6 - hand_len
                    if add_len < len(deck):
                        await self.__hand.add_cards(player, [deck.pop(0) for _ in range(add_len)])
                    else:
                        await self.bot.send_message(self.chat_id, 'Карты в колоде закончились')
                        await self.__hand.add_cards(player, deck)
                        deck = []
            else:
                max_players = database.Chats.get_chat(self.chat_id).max_players
                if hand_len == 0:
                    message_id = await self.__players.get_player_message(player)
                    private_text = ''
                    chat_text = f'{database.Users.get_user(player).username} '

                    if players_len == max_players:
                        private_text = 'Вы выиграли'
                        chat_text += 'выигрывает'
                    else:
                        private_text = 'Вы не выиграли, но и не проиграли'
                        chat_text += 'выбывает'
                    await self.bot.send_message(self.chat_id, chat_text)
                    await self.bot.edit_message_text(private_text, player, message_id)
                    players_len -= 1
                    if players_len == 1:
                        await self.__players.delete_player(player)
                        await self.end()
                        return
                    elif player == struggle:
                        next_struggle = await self._next_player(struggle, 1)
                        next_move = await self._next_player(struggle)
                        await self.__players.delete_player(player)
                    else:
                        await self.__players.delete_player(player)
                        if struggled == 0:
                            await self.__hand.add_cards(struggle, table)
                            next_struggle = await self._next_player(struggle, 1)
                            next_move = await self._next_player(struggle)
                        else:
                            next_struggle = await self._next_player(struggle)
                            next_move = struggle

        await self.__deck.set_cards(deck)

        players = await self.__players.get_players()

        for player in players:
            text = f'Козырь - {str(await self.__state.get_trump_card())}\nКарт в колоде - {len(deck)}'
            message_id = await self.__players.get_player_message(player)
            if player == next_move:
                text = '<strong>Ваш ход</strong>\n\n' + text
            elif player == next_struggle:
                text = '<strong>Вы отбиваетесь</strong>\n\n' + text
            try:
                await self.bot.edit_message_text(text, player, message_id,
                                                 reply_markup=InlineKeyboards.cards_keyboard(self.chat_id,
                                                                                             await self.__hand.get_cards(
                                                                                                 player)))
            except exceptions.MessageNotModified:
                pass

        await self.__table.clear()
        await self.__state.clear_tossed()
        await self.__state.set_struggle(next_struggle)
        await self.__state.set_struggled(1)
        await self.__state.set_next_toss(next_move)
        await self.__state.set_turn(next_move, 'move')
