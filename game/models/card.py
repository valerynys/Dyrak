def id_to_name(id: int) -> str:
    return ["6", "7", "8", "9", "10", "Валет", "Дама", "Король", "Туз"][id-1]


def id_to_suit(id: int) -> str:
    return ["♦", "♥", "♠", "♣"][id-1]


class Card:
    id: int
    name_id: int
    suit_id: int
    name: str
    suit: str

    def __init__(self, name_id: int = None, suit_id: int = None, id: int = None):
        if name_id and suit_id:
            self.id = name_id * 10 + suit_id
            self.name_id = name_id
            self.suit_id = suit_id
        if id:
            self.id = id
            self.name_id = id // 10
            self.suit_id = id % 10
        self.name = id_to_name(self.name_id)
        self.suit = id_to_suit(self.suit_id)

    def __str__(self):
        return f'{self.suit} {self.name}'

    def beat(self, card, trump: int) -> bool:
        if self.suit_id == trump:
            if card.suit_id == trump:
                return self.id > card.id
            return True
        elif self.suit_id == card.suit_id:
            return self.id > card.id
        return False
