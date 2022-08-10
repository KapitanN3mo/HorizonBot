import datetime


def get_msk_datetime() -> datetime.datetime:
    delta = datetime.timedelta(hours=3, minutes=0)
    return (datetime.datetime.now(datetime.timezone.utc) + delta).replace(tzinfo=None)


def get_str_msk_datetime() -> str:
    delta = datetime.timedelta(hours=3, minutes=0)
    return (datetime.datetime.now(datetime.timezone.utc) + delta).strftime(datetime_format)


def get_str_utc_date() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(only_date_format)


def get_str_utc_datetime() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(datetime_format)


datetime_format = '%Y-%m-%d %H:%M'
enchanted_format = '%Y-%m-%d %H:%M:%S'
only_date_format = '%Y-%m-%d'
