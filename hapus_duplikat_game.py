import sqlite3
from konfigurasi import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Hapus duplikat, simpan hanya yang pertama (berdasarkan nama lower+trim)
cur.execute("""
DELETE FROM game
WHERE id NOT IN (
  SELECT MIN(id)
  FROM game
  GROUP BY LOWER(TRIM(nama))
);
""")

conn.commit()
conn.close()
print("✅ Duplikat game dihapus.")
