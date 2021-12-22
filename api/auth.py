from functools import wraps


def auth(func):
    @wraps(func)
    def wrapper(access_level='user'):

