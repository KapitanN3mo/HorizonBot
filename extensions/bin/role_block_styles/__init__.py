class Styles:
    styles = []

    @classmethod
    def add_style(cls, style):
        cls.styles.append(style)

    @classmethod
    def get_style(cls, name):
        for style in cls.styles:
            if style.style_id == name:
                return style
        else:
            return None


class Style:
    __slots__ = ('style_id', 'emojis')


class NumberStyle(Style):
    def __init__(self):
        self.style_id = 'numeric'
        self.emojis = {
            0: '0️⃣',
            1: '1️⃣',
            2: '2️⃣',
            3: '3️⃣',
            4: '4️⃣',
            5: '5️⃣',
            6: '6️⃣',
            7: '7️⃣',
            8: '8️⃣',
            9: '9️⃣'
        }


Styles.add_style(NumberStyle())
