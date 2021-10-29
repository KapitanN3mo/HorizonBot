import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS server_users(
id INTEGER PRIMARY KEY,
message_count INTEGER NOT NULL,
xp INTEGER NOT NULL,
in_voice_time INT NOT NULL,
status TEXT,
warns TEXT,
sys_info TEXT,
last_voice_time TEXT
);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS react_role(
id INT PRIMARY KEY,
info TEXT);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS warns(
id INTEGER PRIMARY KEY,
user INTEGER NOT NULL,
owner INT NOT NULL,
reason TEXT,
datetime TEXT NOT NULL,
expiration INT NOT NULL
);''')
db.commit()
