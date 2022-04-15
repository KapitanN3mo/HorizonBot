from typing import List
from item_grades import *


class Item:

    def __init__(self, name, grade: Grade, display_name: str, image=None):
        self.name = name
        self.image = None
        self.grade = grade
        self.display_name = display_name
        self.id = f'{grade.name}:{name}'
        all_items.append(self)
        print(f'Инициализирован предмет: {self.id}')


all_items: List[Item] = []

wood = Item('wood', ordinary, 'древесина')
stone = Item('stone', ordinary, 'камень')
iron = Item('iron', ordinary, 'железо')
copper = Item('copper', ordinary, 'медь')

glass = Item('glass', extraordinary, 'стекло')
cloth = Item('cloth', extraordinary, 'ткань')

crystal = Item('crystal', rare, 'кристалл')
gold = Item('gold', rare, 'золото')
steel = Item('steel', rare, 'сталь')

amethyst = Item('amethyst', mystical, 'аметист')
emerald = Item('emerald', mystical, 'изумруд')
ruby = Item('ruby', mystical, 'рубин')

soul_core = Item('soul_core', legendary, 'ядро души')
star_shard = Item('star_shard', legendary, 'звёздный осколок')
dark_matter = Item('dark_matter', legendary, 'тёмная материя')

