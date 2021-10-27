import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute('''CREATE IF NOT EXISTS users (
id PRIMARY KEY,
)''')
