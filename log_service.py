import pathlib
from componets import get_msk_datetime, get_str_msk_datetime
import os


class Logging:
    __info_path = pathlib.Path('logs', 'info.log')
    __warning_path = pathlib.Path('Logs', 'warning.log')
    __critical_path = pathlib.Path('Logs', 'critical.log')
    __audit_path = pathlib.Path('Logs', 'audit.log')
    if not os.path.exists('logs'):
        os.mkdir('logs')

    def __init__(self, module_name: str):
        self.name = module_name.upper()

    def audit(self, text: str):
        timestamp = get_str_msk_datetime()
        data = f'{self.name} - {timestamp} - {text}\n'
        with open(self.__audit_path, 'a', encoding='utf-8') as file:
            file.write(data)

    def info(self, text: str):
        timestamp = get_str_msk_datetime()
        data = f'{self.name} - {timestamp} - {text}\n'
        with open(self.__info_path, 'a', encoding='utf-8') as file:
            file.write(data)

    def warning(self, text: str):
        timestamp = get_str_msk_datetime()
        data = f'{self.name} - {timestamp} - {text}\n'
        with open(self.__warning_path, 'a', encoding='utf-8') as file:
            file.write(data)

    def critical(self, text: str):
        timestamp = get_str_msk_datetime()
        data = f'{self.name} - {timestamp} - {text}\n'
        with open(self.__critical_path, 'a', encoding='utf-8') as file:
            file.write(data)
