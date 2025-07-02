# --- manajer.py ---
import datetime, pandas as pd
import database as db
from model import Pelanggan, Game, Transaksi

class GameCenterManager:
    _setup = False
    def __init__(self):
        if not GameCenterManager._setup:
            db.setup_db()
            GameCenterManager._setup = True

    def tambah_pelanggan(self, nama, nomor) -> int | None:
        return db.execute("INSERT INTO pelanggan(nama,nomor) VALUES(?,?)", (nama, nomor))

    def semua_pelanggan(self):
        rows = db.fetch("SELECT * FROM pelanggan")
        return [Pelanggan(r["nama"], r["nomor"], r["id"]) for r in rows] if rows else []

    def tambah_game(self, nama, harga, image_url="") -> int | None:
        nama = nama.strip()
        existing = db.fetch("SELECT id FROM game WHERE LOWER(TRIM(nama))=?", (nama.lower(),), all_=False)
        if existing:
            return None
        return db.execute("INSERT INTO game(nama,harga,image_url) VALUES(?,?,?)",
                          (nama, float(harga), image_url.strip()))

    def semua_game(self):
        rows = db.fetch("SELECT * FROM game")
        return [Game(r["nama"], r["harga"], r["id"], r["image_url"]) for r in rows]

    def tambah_transaksi(self, id_pelanggan: int, id_game: int, jumlah: int, tanggal: datetime.date | None = None) -> bool:
        tanggal = tanggal or datetime.date.today()
        harga_row = db.fetch("SELECT harga FROM game WHERE id=?", (id_game,), all_=False)
        if not harga_row:
            return False
        total = float(harga_row["harga"]) * int(jumlah)
        return db.execute("""
            INSERT INTO transaksi(id_pelanggan,id_game,jumlah,total,tanggal)
            VALUES(?,?,?,?,?)
        """, (id_pelanggan, id_game, jumlah, total, tanggal.strftime("%Y-%m-%d"))) is not None

    def df_transaksi(self, tanggal: datetime.date | None = None) -> pd.DataFrame:
        q = """
            SELECT t.id, p.nama AS pelanggan, p.nomor,
                   g.nama AS game, g.harga, t.jumlah, t.total, t.tanggal
            FROM transaksi t
            JOIN pelanggan p ON p.id = t.id_pelanggan
            JOIN game g ON g.id = t.id_game
        """
        p = None
        if tanggal:
            q += " WHERE t.tanggal=?"
            p = (tanggal.strftime("%Y-%m-%d"),)
        q += " ORDER BY t.tanggal DESC, t.id DESC"
        return pd.read_sql_query(q, db.get_conn(), params=p)

    def total_harian(self, tanggal: datetime.date | None = None) -> float:
        q = "SELECT SUM(total) FROM transaksi"
        p = (tanggal.strftime("%Y-%m-%d"),) if tanggal else None
        row = db.fetch(q + (" WHERE tanggal=?" if tanggal else ""), p, all_=False)
        return float(row[0]) if row and row[0] else 0.0

    def total_per_game(self, tanggal: datetime.date | None = None) -> dict:
        q = """
            SELECT g.nama, SUM(t.total) AS tot FROM transaksi t
            JOIN game g ON g.id=t.id_game
        """
        p = []
        if tanggal:
            q += " WHERE t.tanggal=?"
            p.append(tanggal.strftime("%Y-%m-%d"))
        q += " GROUP BY g.id ORDER BY tot DESC"
        rows = db.fetch(q, tuple(p) if p else None)
        return {r["nama"]: float(r["tot"]) for r in rows} if rows else {}
