import sqlite3

connection = sqlite3.connect('database/database.db')

cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    purchase_price REAL NOT NULL,
    selling_price REAL NOT NULL
)
''')

connection.commit()

connection.close()

print("Tabela products criada com sucesso!")
