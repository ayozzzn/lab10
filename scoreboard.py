import psycopg2
from tabulate import tabulate

conn = psycopg2.connect(
    dbname = 'snake',
    user = 'postgres',
    password = '',
    host = 'localhost',
    port = 5432
)
cur = conn.cursor()

cur.execute("""
SELECT gu.username, gs.score, gs.level, gs.saved_at
FROM game_score gs
JOIN game_user gu ON gs.user_id = gu.user_id
ORDER BY gs.saved_at DESC;
""")

rows = cur.fetchall()
print(tabulate(rows, headers=["Username", "Score", "Level", "Saved At"], tablefmt="fancy_grid"))

cur.close()
conn.close()