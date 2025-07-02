# konfigurasi_game.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = "game_center.db"
DB_PATH  = os.path.join(BASE_DIR, DB_NAME)

KATEGORI_DEFAULT = "Umum"          # tidak terlalu dipakai di skema baru, tapi disiapkan
LOCALE_ID = "id_ID.UTF-8"          # dipakai untuk format Rupiah
