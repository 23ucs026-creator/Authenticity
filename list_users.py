import sqlite3

conn = sqlite3.connect("instance/auth_validator.db")
cur = conn.cursor()

rows = cur.execute("SELECT id, username, email FROM user").fetchall()

print("Users in database:")
for r in rows:
    print(r)
