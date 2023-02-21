import random
import time
from typing import List

from .card import Card


class Deck:
    cards: List[Card] = []
    chat_id: int

    def __init__(self, chat_id: int):
        for i in range(1, 10):
            for j in range(1, 5):
                self.cards.append(Card(i, j))
        self.chat_id = chat_id
        self.shuffle()

    def shuffle(self) -> None:
        random.seed(int(str(self.chat_id) + str(int(time.time()))))
        random.shuffle(self.cards)

    def pop_cards(self, count: int) -> List[Card]:
        return [self.cards.pop(0) for _ in range(count)]

    def get_trump_card(self) -> Card:
        return self.cards[-1]
