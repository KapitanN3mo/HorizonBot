import discord


class Warrior:
    def __init__(self, name, emoji):
        self._name = name
        self._emoji = emoji
        self._state = False
        self._owner = None

    @property
    def owner(self):
        return self._owner

    @property
    def emoji(self):
        return self._emoji

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def set_state(self, state: bool):
        self._state = state

    def set_owner(self, owner):
        self._owner = owner

    def is_ready(self):
        return self._state


class CrusaderTeam:
    def __init__(self):
        self.knight = Warrior('Рыцарь', '⚔'),
        self.inquisitor = Warrior('Инквизитор', '🔮'),
        self.archer = Warrior('Лучник', '🏹'),
        self.healer = Warrior('Лекарь', '💉'),
        self.cartographer = Warrior('Картограф-проводник', '🗺'),
        self.scout = Warrior('Разведчик', '🔎')
        self.alchemist = Warrior('Алхимик', '🧪')

    def get_by_name(self, name: str):
        for wr in self.get_warriors_list():
            if wr.name == name:
                result = wr
                break
        else:
            result = None
        return result

    def get_by_emoji(self, emoji: str):
        for wr in self.get_warriors_list():
            if wr.emoji == emoji:
                result = wr
                break
        else:
            result = None
        return result

    def get_all(self):
        return self.get_warriors_list()

    def set_owner(self, owner, name=None, emoji=None):
        if name is not None:
            wr = self.get_by_name(name)
        elif emoji is not None:
            wr = self.get_by_emoji(emoji)
        else:
            return False
        if wr is not None:
            wr.set_state = True
            wr.set_owner(owner)

    def del_owner(self, name=None, emoji=None):
        if name is not None:
            wr = self.get_by_name(name)
        elif emoji is not None:
            wr = self.get_by_emoji(emoji)
        else:
            return False
        if wr is not None:
            wr.set_state = False
            wr.set_owner(None)

    def get_string(self):
        wr_string = ''
        for warrior in self.get_warriors_list():
            if warrior.owner is None:
                owner_name = 'свободный'
            else:
                owner_name = warrior.owner.display_name
            wr_string += f'{warrior.emoji} {warrior.name}:  {owner_name}\n'
        return wr_string

    def get_warriors_list(self):
        warrior_list = []
        for warrior in [self.__dict__[i] for i in self.__dict__]:
            if isinstance(warrior, tuple):
                if isinstance(warrior[0], Warrior):
                    warrior = warrior[0]
            elif isinstance(warrior, Warrior):
                pass
            else:
                continue
            warrior_list.append(warrior)
        return warrior_list

    def is_ready(self):
        return all([wr.is_ready() for wr in self.get_warriors_list()])


if __name__ == '__main__':
    s = CrusaderTeam()
    print(s.get_string())
