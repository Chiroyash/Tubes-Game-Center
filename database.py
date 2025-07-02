import sqlite3, logging
from konfigurasi import DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_conn():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Koneksi DB gagal: {e}")
        return None

def execute(q, p=None):
    conn = get_conn()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute(q, p or ())
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Query gagal: {e} | {q[:60]}")
        conn.rollback()
        return None
    finally:
        conn.close()

def fetch(q, p=None, all_=True):
    conn = get_conn()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute(q, p or ())
        return cur.fetchall() if all_ else cur.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Fetch gagal: {e} | {q[:60]}")
        return None
    finally:
        conn.close()

def setup_db():
    logger.info(f"➡️  Setup DB di {DB_PATH}")
    sql = [
        """CREATE TABLE IF NOT EXISTS pelanggan(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nomor TEXT NOT NULL UNIQUE
        );""",
        """CREATE TABLE IF NOT EXISTS game(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL UNIQUE,
            harga REAL NOT NULL CHECK(harga>0)
        );""",
        """CREATE TABLE IF NOT EXISTS transaksi(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pelanggan INTEGER NOT NULL,
            id_game INTEGER NOT NULL,
            jumlah INTEGER NOT NULL CHECK(jumlah>0),
            total REAL NOT NULL,
            tanggal DATE NOT NULL,
            FOREIGN KEY(id_pelanggan) REFERENCES pelanggan(id),
            FOREIGN KEY(id_game) REFERENCES game(id)
        );"""
    ]
    for s in sql: execute(s)
    logger.info("✅  Tabel siap.")
