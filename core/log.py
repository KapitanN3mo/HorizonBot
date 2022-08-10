import os.path
import sys

import colorama

import dt


class LogLevel:
    def __init__(self, name, level, color):
        self.name: str = name
        self.lvl: int = level
        self.color: colorama.Fore = color

    def to_file(self):
        return f'[{self.name}] '

    def to_console(self):
        return f'{self.color}[{self.name}]{colorama.Style.RESET_ALL}'


DEBUG = LogLevel('DEBUG', 0, colorama.Fore.BLUE)
INFO = LogLevel('INFO', 1, colorama.Fore.GREEN)
WARNING = LogLevel('WARNING', 2, colorama.Fore.YELLOW)
ERROR = LogLevel('ERROR', 3, colorama.Fore.RED)


class Logger:
    console_level: LogLevel = DEBUG
    file_level: LogLevel = INFO
    root = os.path.abspath(sys.argv[0].replace('main.py', ''))

    def __init__(self, service_name):
        self.service_name = service_name

    @classmethod
    def _check_level(cls, level: LogLevel, out: str) -> bool:
        tl = cls.console_level.lvl if out == "console" else cls.file_level.lvl
        return level.lvl >= tl

    def _write_to_file(self, level: LogLevel, message):
        self._check_dir()
        if self._check_level(level, 'file'):
            with open(self._get_file_name(), 'a') as file:
                file.write(f'\n{level.to_file()}[{self.service_name}] {dt.get_str_utc_datetime()} {message}')

    def _write_to_console(self, level: LogLevel, message):
        if self._check_level(level, 'console'):
            print(f'{level.to_console()}[{self.service_name}] {dt.get_str_utc_datetime()} {message}')

    @classmethod
    def _get_file_name(cls) -> str:
        return os.path.join(cls.root, f'{dt.get_str_utc_date()}.log')

    @classmethod
    def _check_dir(cls):
        if not os.path.exists(os.path.join(cls.root, "logs")) or not os.path.isdir(os.path.join(cls.root, 'logs')):
            os.mkdir(os.path.join(cls.root, 'logs'))

    def info(self, message: str):
        self._write_to_console(INFO, message)
        self._write_to_file(INFO, message)

    def debug(self, message: str):
        self._write_to_console(DEBUG, message)
        self._write_to_file(DEBUG, message)

    def warning(self, message: str):
        self._write_to_console(WARNING, message)
        self._write_to_file(WARNING, message)

    def error(self, message: str):
        self._write_to_console(ERROR, message)
        self._write_to_file(ERROR, message)
