import os
import platform
import psycopg2
from psycopg2 import sql

pf = platform.system()
if pf == 'Windows':
    db = psycopg2.connect(host='127.0.0.1',
                          port=5432,
                          database='horizon_bot',
                          user='test',
                          password='qwerty')
    flask_db = psycopg2.connect(host='127.0.0.1',
                                port=5432,
                                database='horizon_bot',
                                user='test',
                                password='qwerty')
else:
    DATABASE_URL = os.environ['DATABASE_URL']
    db = psycopg2.connect(DATABASE_URL, sslmode='require')
    db.set_session(autocommit=True)
    flask_db = psycopg2.connect(DATABASE_URL, sslmode='require')
    flask_db.set_session(autocommit=True)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS server_users(
id BIGINT PRIMARY KEY,
message_count INTEGER NOT NULL,
xp INTEGER NOT NULL,
in_voice_time INT NOT NULL,
status TEXT,
warns TEXT,
sys_info TEXT,
last_voice_time TEXT
);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS react_role(
id BIGINT PRIMARY KEY,
info TEXT);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS warns(
id SERIAL PRIMARY KEY,
"user" BIGINT NOT NULL,
owner BIGINT NOT NULL,
reason TEXT,
datetime TEXT NOT NULL,
expiration INT NOT NULL
);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS error_rep(
id SERIAL PRIMARY KEY,
info TEXT NOT NULL,
status INT NOT NULL,
datetime TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS api_tokens(
id BIGINT PRIMARY KEY,
name TEXT,
token TEXT)
''')
cursor.execute('''CREATE TABLE IF NOT EXISTS tasks(
id SERIAL PRIMARY KEY,
owner BIGINT NOT NULL,
created_time timestamp NOT NULL,
expiration_time timestamp NOT NULL,
task_info json NOT NULL);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS rules(
guild_id BIGINT NOT NULL,
message_id BIGINT NOT NULL,
title TEXT NOT NULL,
content TEXT NOT NULL,
owner BIGINT NOT NULL);
''')
db.commit()
