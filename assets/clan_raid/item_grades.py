import typing


class Grade:
    def __init__(self, display_name: str, color: int, grade_id: str):
        self.name = grade_id
        self.color = color
        self.display_name = display_name
        all_grades.append(self)
        print(f'Инициализирован грейд (предметы): {self.name}')


all_grades: typing.List[Grade] = []

ordinary = Grade('обычный', 0x444444, 'ordinary')
extraordinary = Grade('необычный', 0x00DB6A, 'extraordinary')
rare = Grade('редкий', 0x2E2EFF, 'rare')
mystical = Grade('мифический', 0xFF742E, 'mystical')
legendary = Grade('легендарный', 0x6A0092, 'legendary')
