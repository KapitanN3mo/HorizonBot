import datetime
import configparser


def get_msk_datetime() -> datetime.datetime:
    delta = datetime.timedelta(hours=3, minutes=0)
    return datetime.datetime.now(datetime.timezone.utc) + delta


def get_str_msk_datetime() -> str:
    delta = datetime.timedelta(hours=3, minutes=0)
    return (datetime.datetime.now(datetime.timezone.utc) + delta).strftime('%Y-%m-%d-%H-%M')


def convert_number_to_emoji(number: int):
    num_emoji = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣',
                 9: '9️⃣'}
    if number in num_emoji:
        return num_emoji[number]
    else:
        return None


class ConfigWithCommit():
    def __init__(self, path):
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(path)

    def set(self, section: str, option: str, value: str):
        self.config.set(section, option, value)
        self.commit()

    def get(self, section, option) -> str:
        value = self.config.get(section, option)
        return value

    def add_section(self, section):
        self.config.add_section(section)
        self.commit()

    def remove_section(self, section):
        self.config.remove_section(section)
        self.commit()

    def commit(self):
        with open(self.path, 'w') as file:
            self.config.write(file)


config = ConfigWithCommit('configuration.ini')
temp_file = ConfigWithCommit('temp.ini')
datetime_format = '%Y-%m-%d-%H-%M'
