import sqlite3

connection = sqlite3.connect("crypto.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS crypto_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    coin_name TEXT,
    symbol TEXT,
    price TEXT,
    change_24h TEXT,
    market_cap TEXT
)
""")

connection.commit()
connection.close()

print("Database created successfully!")
print("Database: crypto.db")
print("Table: crypto_prices")