import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("SELECT * FROM users")
print(*c.fetchall(), sep='\n')
#c.execute("DELETE FROM users WHERE id=1480780006")
#c.execute("DELETE FROM users WHERE id=1814535647")
#c.execute("DELETE FROM users WHERE id=860405512")
#c.execute("DELETE FROM users WHERE id=446836073")
#c.execute("DELETE FROM users WHERE id=502436052")
conn.commit()
conn.close()
