import peewee
import dt

db = peewee.PostgresqlDatabase(host='127.0.0.1',
                               port=5432,
                               database='horizon_bot',
                               user='horizon_bot',
                               password='s24d300')


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Guild(BaseModel):
    guild_id = peewee.BigIntegerField(primary_key=True)
    admins = peewee.TextField(null=False)
    rules = peewee.TextField(null=True)
    notify_channel = peewee.BigIntegerField(null=True)
    clan_channel = peewee.BigIntegerField(null=True)
    bot_channel = peewee.BigIntegerField(null=True)
    private_voice = peewee.BigIntegerField(null=True)

    minimum_voice_time = peewee.IntegerField(null=False, default=10)
    xp_voice_multiplier = peewee.FloatField(null=False, default=1)
    xp_message_multiplier = peewee.FloatField(null=False, default=1)

    min_work_cash = peewee.IntegerField(default=100)
    max_work_cash = peewee.IntegerField(default=400)
    work_delay = peewee.IntegerField(default=30)

    min_gachi_cash = peewee.IntegerField(default=1000)
    max_gachi_cash = peewee.IntegerField(default=5000)
    gachi_delay = peewee.IntegerField(default=60)
    gachi_delay_after_fail = peewee.IntegerField(default=1440)
    ass_breaking_chance = peewee.IntegerField(default=80)

    min_crime_cash = peewee.IntegerField(default=500)
    max_crime_cash = peewee.IntegerField(default=1000)
    crime_delay = peewee.IntegerField(default=180)
    crime_fail_chance = peewee.IntegerField(default=30)

    steal_fail_chance = peewee.IntegerField(default=50)
    max_steal_fail_loss = peewee.IntegerField(default=100)
    min_steal_fail_loss = peewee.IntegerField(default=30)
    max_steal_lucky_loss = peewee.IntegerField(default=100)
    min_steal_lucky_loss = peewee.IntegerField(default=50)

    coin_name = peewee.TextField(default='Coin')


class User(BaseModel):
    user_db_id = peewee.AutoField(primary_key=True)
    user_id = peewee.BigIntegerField(null=False)
    guild_id = peewee.ForeignKeyField(Guild, null=False, to_field='guild_id')
    message_count = peewee.IntegerField(null=False)
    xp = peewee.IntegerField(null=False)
    in_voice_time = peewee.IntegerField(null=False)
    send_voice_report = peewee.BooleanField(default=True)
    discord_name = peewee.TextField(null=False)

    money = peewee.IntegerField(default=0, null=False)
    bank = peewee.BigIntegerField(default=0)

    last_work_use = peewee.TimestampField(null=False, default=0)
    last_gachi_use = peewee.TimestampField(null=False, default=0)
    last_crime_use = peewee.TimestampField(null=False, default=0)
    is_ass_breaking = peewee.BooleanField(null=False, default=False)

    class Meta:
        table_name = 'users'
        indexes = (
            (('user_id', 'guild_id'), True),
        )


class RoleBlock(BaseModel):
    block_id = peewee.AutoField(primary_key=True)
    name = peewee.TextField(null=False)
    color = peewee.IntegerField(null=False)
    style = peewee.TextField(null=True)
    guild = peewee.ForeignKeyField(Guild, null=False)
    block_channel_id = peewee.BigIntegerField(null=True)
    block_message_id = peewee.BigIntegerField(null=True, unique=True)


class Role(BaseModel):
    role_id = peewee.BigIntegerField(primary_key=True)
    guild = peewee.ForeignKeyField(Guild, null=False)
    name = peewee.TextField(null=False)
    linked_block = peewee.ForeignKeyField(RoleBlock, null=True)
    position = peewee.IntegerField(null=True)
    color = peewee.TextField(null=False)
    emoji = peewee.TextField(null=True)
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


class Clan(BaseModel):
    clan_id = peewee.AutoField(primary_key=True)
    guild = peewee.ForeignKeyField(Guild, null=False)
    owner = peewee.ForeignKeyField(User, null=False)
    name = peewee.TextField(null=False, unique=True)
    tag = peewee.TextField(null=False, unique=True)
    color = peewee.IntegerField(null=False)
    description = peewee.TextField(null=False)
    emblem = peewee.TextField(null=False)
    created_date = peewee.TimestampField(default=dt.get_msk_datetime(), null=False)
    level = peewee.IntegerField(null=False, default=0)
    verify = peewee.BooleanField(null=False, default=False)
    verify_issuing = peewee.ForeignKeyField(User, null=True)


class Inventory(BaseModel):
    item_id = peewee.TextField(null=False)
    count = peewee.IntegerField(null=False)
    clan = peewee.ForeignKeyField(Clan, null=False)


class ClanMember(BaseModel):
    user = peewee.ForeignKeyField(User, primary_key=True)
    clan = peewee.ForeignKeyField(Clan, null=False)
    class_ = peewee.TextField(null=False)


class VoiceJournal(BaseModel):
    identity = peewee.BigAutoField()
    user = peewee.ForeignKeyField(User, null=False)
    timestamp = peewee.TimestampField(default=dt.get_msk_datetime())
    data = peewee.TextField(null=False)


class Schedule(BaseModel):
    identity = peewee.AutoField(primary_key=True)
    guild = peewee.ForeignKeyField(Guild, null=False)
    expiration = peewee.TimestampField(null=True)
    author = peewee.ForeignKeyField(User, null=False)
    name = peewee.TextField(null=False)

    class Meta:
        indexes = (
            (('name', 'guild'), True),
        )


class Task(BaseModel):
    identity = peewee.AutoField(primary_key=True)
    task_number = peewee.IntegerField(null=False)
    schedule = peewee.ForeignKeyField(Schedule, null=False)
    text = peewee.TextField(null=False)
    executor = peewee.ForeignKeyField(User, null=False)
    status = peewee.TextField(null=False, default='created')
    author = peewee.ForeignKeyField(User, null=False)


Guild.create_table()
User.create_table()
Warn.create_table()
TextBotMessage.create_table()
ApiUser.create_table()
MarryPartner.create_table()
RoleBlock.create_table()
Role.create_table()
Clan.create_table()
ClanMember.create_table()
VoiceJournal.create_table()
Schedule.create_table()
Task.create_table()
