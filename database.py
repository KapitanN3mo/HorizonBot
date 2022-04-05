import os
import platform
import peewee
import dt

pf = platform.system()
if pf == 'Windows':
    db = peewee.PostgresqlDatabase(host='127.0.0.1',
                                   port=5432,
                                   database='horizon_bot',
                                   user='HorizonBot',
                                   password='s24d300')

else:
    DATABASE_URL = os.environ['DATABASE_URL']
    db = peewee.PostgresqlDatabase(DATABASE_URL, sslmode='require')
db.autorollback = True


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Guild(BaseModel):
    guild_id = peewee.BigIntegerField(primary_key=True)
    admins = peewee.TextField(null=False)
    rules = peewee.TextField(null=True)
    notify_channel = peewee.BigIntegerField(null=True)
    bot_channel = peewee.BigIntegerField(null=True)
    role_channel = peewee.BigIntegerField(null=True)
    mute_role = peewee.BigIntegerField(null=True)
    private_voice = peewee.BigIntegerField(null=True)
    minimum_voice_time = peewee.IntegerField(null=False, default=10)
    xp_voice_multiplier = peewee.FloatField(null=False, default=1)
    xp_message_multiplier = peewee.FloatField(null=False, default=1)
    statistics_category = peewee.BigIntegerField(null=True)
    statistics_info = peewee.TextField(null=True)
    day_message = peewee.IntegerField(null=True)
    webhook = peewee.TextField(null=True)


class User(BaseModel):
    user_db_id = peewee.AutoField(primary_key=True)
    user_id = peewee.BigIntegerField(null=False)
    guild_id = peewee.ForeignKeyField(Guild, null=False, to_field='guild_id')
    message_count = peewee.IntegerField(null=False)
    xp = peewee.IntegerField(null=False)
    in_voice_time = peewee.IntegerField(null=False)
    sys_info = peewee.TextField(null=False)
    voice_entry = peewee.TimestampField(null=True)
    discord_name = peewee.TextField(null=False)

    class Meta:
        table_name = 'users'
        indexes = (
            (('user_id', 'guild_id'), True),
        )


class RoleBlock(BaseModel):
    block_id = peewee.AutoField(primary_key=True)
    name = peewee.TextField(null=False)
    color = peewee.TextField(null=False)
    style = peewee.TextField(null=True)
    guild = peewee.ForeignKeyField(Guild, null=False)
    block_message_id = peewee.BigIntegerField(null=True, unique=True)


class Role(BaseModel):
    role_id = peewee.BigIntegerField(primary_key=True)
    guild = peewee.ForeignKeyField(Guild, null=False)
    name = peewee.TextField(null=False)
    linked_block = peewee.ForeignKeyField(RoleBlock, null=True)
    color = peewee.TextField(null=False)
    custom_emoji = peewee.TextField(null=True)
    having_users = peewee.TextField(null=False)


class MarryPartner(BaseModel):
    user1 = peewee.ForeignKeyField(User, null=False)
    user2 = peewee.ForeignKeyField(User, null=False)
    date = peewee.TimestampField(null=False, default=dt.get_msk_datetime())


class Warn(BaseModel):
    warn_id = peewee.AutoField(primary_key=True, column_name='warn_id')
    guild_id = peewee.ForeignKeyField(Guild, null=False, column_name='guild_id')
    user_db_id = peewee.ForeignKeyField(User, null=False, column_name='user_id')
    owner_id = peewee.ForeignKeyField(User, null=False, column_name='owner_id')
    reason = peewee.TextField(null=False, column_name='reason')
    datetime = peewee.TimestampField(null=False, column_name='datetime')
    expiration = peewee.IntegerField(null=False, column_name='expiration')


class TextBotMessage(BaseModel):
    message_id = peewee.BigIntegerField(primary_key=True, column_name='message_id')
    guild_id = peewee.ForeignKeyField(Guild, column_name='guild_id', null=False)
    channel_id = peewee.BigIntegerField(column_name='channel_id', null=False)
    author_id = peewee.ForeignKeyField(User, column_name='owner_id', null=False)
    send_time = peewee.TimestampField(column_name='send_time', default=dt.get_msk_datetime())


class ApiUser(BaseModel):
    user_id = peewee.BigIntegerField(primary_key=True)
    user_name = peewee.TextField(null=False, column_name='user_name')
    password_hash = peewee.TextField(null=False)
    user_type = peewee.TextField(null=False, column_name='user_type')
    refresh_token = peewee.TextField(null=True)


class FunData(BaseModel):
    data = peewee.TextField(null=False)


Guild.create_table()
User.create_table()
Warn.create_table()
TextBotMessage.create_table()
ApiUser.create_table()
MarryPartner.create_table()
RoleBlock.create_table()
Role.create_table()
