# model_game.py
import datetime, locale
from konfigurasi import LOCALE_ID

def _format_rp(x):
    try:
        locale.setlocale(locale.LC_ALL, LOCALE_ID)
        return locale.currency(x, grouping=True, symbol="Rp ")[:-3]
    except:
        return f"Rp {x:,.0f}".replace(",", ".")

class Pelanggan:
    def __init__(self, nama: str, nomor: str, id_: int | None = None):
        self.id = id_
        self.nama = nama.strip()
        self.nomor = nomor.strip()
    def __repr__(self):
        return f"Pelanggan({self.id}, {self.nama}, {self.nomor})"

class Game:
    def __init__(self, nama: str, harga: float, id_: int | None = None, image_url: str | None = None):
        self.id = id_
        self.nama = nama.strip()
        self.harga = float(harga)
        self.image_url = image_url or ""
    def __repr__(self):
        return f"Game({self.id}, {self.nama}, {self.harga}, {self.image_url})"

class Transaksi:
    def __init__(self, pelanggan: Pelanggan, game: Game, jumlah: int,
                 tanggal: datetime.date | str, id_: int | None = None):
        self.id = id_
        self.pelanggan = pelanggan
        self.game = game
        self.jumlah = int(jumlah)
        self.tanggal = (
            tanggal if isinstance(tanggal, datetime.date)
            else datetime.datetime.strptime(tanggal, "%Y-%m-%d").date()
        )
        self.total = self.jumlah * self.game.harga
    def __repr__(self):
        return (f"Tx({self.id}) {self.tanggal} – {self.pelanggan.nama} "
                f"main {self.jumlah}×{self.game.nama} → {_format_rp(self.total)})")
