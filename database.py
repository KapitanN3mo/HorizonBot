import os
import platform
import peewee
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import modules.datetime

pf = platform.system()
if pf == 'Windows':
    db = peewee.PostgresqlDatabase(host='127.0.0.1',
                                   port=5432,
                                   database='horizon_bot',
                                   user='test',
                                   password='qwerty')

else:
    DATABASE_URL = os.environ['DATABASE_URL']
    db = peewee.PostgresqlDatabase(DATABASE_URL, sslmode='require')
db.autorollback = True


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = peewee.BigIntegerField(primary_key=True)
    message_count = peewee.IntegerField(null=False)
    xp = peewee.IntegerField(null=False)
    in_voice_time = peewee.IntegerField(null=False)
    sys_info = peewee.TextField(null=False)
    voice_entry = peewee.TimestampField(null=True)

    class Meta:
        table_name = 'users'


class Task(BaseModel):
    task_id = peewee.AutoField(primary_key=True, column_name='task_id')
    owner_id = peewee.ForeignKeyField(User, null=False, column_name='owner_id')
    created_time = peewee.TimestampField(null=False, column_name='created_time')
    event_time = peewee.TimestampField(null=False, column_name='event_time')
    task_type = peewee.TextField(null=False, column_name='task_type')
    task_info = peewee.TextField(null=False, column_name='task_info')

    class Meta:
        table_name = 'tasks'


class Guild(BaseModel):
    guild_id = peewee.BigIntegerField(primary_key=True, column_name='guild_id')
    admins = peewee.TextField(null=False, column_name='admins')
    rules = peewee.TextField(null=True, column_name='rules')
    notify_channel = peewee.BigIntegerField(null=True, column_name='notify_channel')
    bot_channel = peewee.BigIntegerField(null=True, column_name='bot_channel')
    game_channel = peewee.BigIntegerField(null=True, column_name='game_channel')
    mute_role = peewee.BigIntegerField(null=True, column_name='mute_role')
    private_voice = peewee.BigIntegerField(null=True, column_name='private_voice')
    minimum_voice_time = peewee.IntegerField(null=False, column_name='minimum_voice_time', default=10)
    xp_voice_multiplier = peewee.FloatField(null=False, column_name='xp_voice_multiplier', default=1)
    xp_message_multiplier = peewee.FloatField(null=False, column_name='xp_message_multiplier', default=1)

    class Meta:
        table_name = 'guilds'


class Warn(BaseModel):
    warn_id = peewee.AutoField(primary_key=True, column_name='warn_id')
    guild_id = peewee.ForeignKeyField(Guild, column_name='guild_id', null=False)
    user_id = peewee.ForeignKeyField(User, null=False, column_name='user_id')
    owner_id = peewee.ForeignKeyField(User, null=False, column_name='owner_id')
    reason = peewee.TextField(null=False, column_name='reason')
    datetime = peewee.TimestampField(null=False, column_name='datetime')
    expiration = peewee.IntegerField(null=False, column_name='expiration')

    class Meta:
        table_name = 'warns'


class PrivateChannel(BaseModel):
    channel_id = peewee.BigIntegerField(primary_key=True, column_name='channel_id')
    owner_id = peewee.ForeignKeyField(User, null=False, column_name='owner_id')
    guild_id = peewee.ForeignKeyField(Guild, null=False, column_name='guild_id')

    class Meta:
        table_name = 'private_channels'


class BotMessage(BaseModel):
    message_id = peewee.BigIntegerField(primary_key=True, column_name='message_id')
    guild_id = peewee.ForeignKeyField(Guild, column_name='guild_id', null=False)
    channel_id = peewee.BigIntegerField(column_name='channel_id', null=False)
    owner_id = peewee.ForeignKeyField(User, column_name='owner_id', null=False)
    message_type = peewee.TextField(column_name='message_type', null=False)
    send_time = peewee.TimestampField(column_name='send_time', null=False, default=modules.datetime.get_msk_datetime())
    message_data = peewee.TextField(column_name='message_data', null=False)

    class Meta:
        table_name = 'bot_messages'


class Journal(BaseModel):
    action_id = peewee.BigAutoField(primary_key=True, column_name='action_id')
    timestamp = peewee.TimestampField(column_name='timestamp', null=False, default=modules.datetime.get_msk_datetime())
    action_type = peewee.TextField(column_name='action_type', null=False)
    action_data = peewee.TextField(column_name='action_data', null=False)

    class Meta:
        table_name = 'journal'


class ApiUser(BaseModel):
    user_id = peewee.BigIntegerField(primary_key=True, column_name='user_id')
    user_name = peewee.TextField(null=False, column_name='user_name')
    password_hash = peewee.TextField(null=False)
    user_type = peewee.TextField(null=False, column_name='user_type')
    refresh_token = peewee.TextField(null=True)

    class Meta:
        table_name = 'api_users'


User.create_table()
Guild.create_table()
Warn.create_table()
Task.create_table()
PrivateChannel.create_table()
BotMessage.create_table()
Journal.create_table()
ApiUser.create_table()

if __name__ == '__main__':
    us = ApiUser.create(user_id=990988,
                        user_name='test',
                        password_hash=generate_password_hash('qwerty'),
                        user_type='user')
