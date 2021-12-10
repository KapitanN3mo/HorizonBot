import os
import platform
import peewee

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


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = peewee.BigIntegerField(column_name='user_id', primary_key=True)
    message_count = peewee.IntegerField(column_name='message_count', null=False)
    xp = peewee.IntegerField(column_name='xp', null=False)
    in_voice_time = peewee.IntegerField(column_name='in_voice_time', null=False)
    sys_info = peewee.TextField(column_name='sys_info', null=False)
    last_voice_time = peewee.TimestampField(column_name='last_voice_time', null=False)

    class Meta:
        table_name = 'server_users'


class Warns(BaseModel):
    warn_id = peewee.AutoField(primary_key=True, column_name='warn_id')
    user = peewee.ForeignKeyField(Users, to_field='user_id', null=False, column_name='user')
    owner = peewee.ForeignKeyField(Users, to_field='user_id', null=False, column_name='owner')
    reason = peewee.TextField(null=False, column_name='reason')
    datetime = peewee.TimestampField(null=False, column_name='datetime')
    expiration = peewee.IntegerField(null=False, column_name='expiration')

    class Meta:
        table_name = 'warns'


class Tasks(BaseModel):
    task_id = peewee.AutoField(primary_key=True, column_name='task_id')
    owner = peewee.ForeignKeyField(Users, to_field='user_id', null=False, column_name='owner')
    created_time = peewee.TimestampField(null=False, column_name='created_time')
    event_time = peewee.TimestampField(null=False, column_name='event_time')
    task_type = peewee.TextField(null=False, column_name='task_type')
    task_info = peewee.TextField(null=False, column_name='task_info')

    class Meta:
        table_name = 'tasks'


class Servers(BaseModel):
    server_id = peewee.BigIntegerField(primary_key=True, column_name='server_id')
    admins = peewee.TextField(null=False, column_name='admins')
    rules = peewee.TextField(null=True, column_name='rules')
    notify_channel = peewee.BigIntegerField(null=True, column_name='notify_channel')
    bot_channel = peewee.BigIntegerField(null=True, column_name='bot_channel')
    game_channel = peewee.BigIntegerField(null=True, column_name='game_channel')

    class Meta:
        table_name = 'servers'


Users.create_table()
Warns.create_table()
Tasks.create_table()
Servers.create_table()


