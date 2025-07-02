import sqlite3
from konfigurasi import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DELETE FROM pelanggan")
cur.execute("DELETE FROM game")
cur.execute("DELETE FROM transaksi")
conn.commit()
conn.close()
print("✅ Semua data game telah dihapus.")
