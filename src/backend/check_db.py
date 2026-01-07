import sqlite3

conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(loan)')
print('Loan table columns:')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')
conn.close()
