import datetime


def get_msk_datetime() -> datetime.datetime:
    delta = datetime.timedelta(hours=3, minutes=0)
    return (datetime.datetime.now(datetime.timezone.utc) + delta).replace(tzinfo=None)


def get_str_msk_datetime() -> str:
    delta = datetime.timedelta(hours=3, minutes=0)
    return (datetime.datetime.now(datetime.timezone.utc) + delta).strftime('%Y-%m-%d-%H-%M')

datetime_format = '%Y-%m-%d-%H-%M'