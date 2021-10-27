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
last_voice_time
);''')
db.commit()

