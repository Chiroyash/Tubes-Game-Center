# --- main_app.py ---
import streamlit as st, datetime, pandas as pd, locale, os
from konfigurasi import LOCALE_ID
from manajer import GameCenterManager

st.set_page_config(page_title="Game Center Ledger", layout="wide")

def rp(x):
    try: locale.setlocale(locale.LC_ALL, LOCALE_ID)
    except: pass
    try: return locale.currency(x, grouping=True, symbol="Rp ")[:-3]
    except: return f"Rp {x:,.0f}".replace(",", ".")

m = GameCenterManager()

# --- Inisialisasi game default (sekali saja) ---
if "game_sudah_diisi" not in st.session_state:
    daftar_awal_game = [
        ("Mobile Legends", 5000, "gambar/ml.jpg"),
        ("PUBG Mobile", 6000, "gambar/pubg.jpg"),
        ("Free Fire", 4000, "gambar/ff.jpg"),
        ("Genshin Impact", 7000, "gambar/genshin.jpg"),
        ("Valorant", 8000, "gambar/valorant.jpg"),
        ("Fortnite", 7500, "gambar/fortnite.jpg"),
        ("Minecraft", 5000, "gambar/minecraft.jpg"),
        ("Call of Duty Mobile", 6500, "gambar/cod.jpg"),
        ("Clash of Clans", 3000, "gambar/coc.jpg"),
        ("Clash Royale", 3000, "gambar/cr.jpg"),
        ("Apex Legends", 8500, "gambar/apex.jpg"),
        ("League of Legends", 8000, "gambar/lol.jpg"),
        ("Dota 2", 7500, "gambar/dota.jpg"),
        ("Arena of Valor", 5500, "gambar/arena.jpg"),
        ("Honkai: Star Rail", 7000, "gambar/honkai.jpg"),
        ("Roblox", 4000, "gambar/roblox.png"),
        ("Subway Surfers", 2000, "gambar/subway.jpg"),
        ("Among Us", 3500, "gambar/among.jpg"),
        ("Stumble Guys", 3000, "gambar/stumble.jpg"),
        ("Brawl Stars", 3500, "gambar/brawl.png"),
    ]
    nama_game_db = [g.nama.strip().lower() for g in m.semua_game()]
    for nama, harga, url in daftar_awal_game:
        if nama.strip().lower() not in nama_game_db:
            m.tambah_game(nama, harga, url)
    st.session_state["game_sudah_diisi"] = True

menu = st.sidebar.radio("Menu", ["Pelanggan", "Game", "Transaksi", "Riwayat", "Ringkasan"])

if menu == "Game":
    st.header("\U0001F3AE Pilih Game")
    daftar_game = m.semua_game()
    if not daftar_game:
        st.warning("Belum ada game yang tersedia.")
    else:
        col_per_row = 4
        cols = st.columns(col_per_row)

        seen = set()
        game_unik = []
        for g in daftar_game:
            key = g.nama.strip().lower()
            if key not in seen:
                seen.add(key)
                game_unik.append(g)

        for i, game in enumerate(game_unik):
            with cols[i % col_per_row]:
                st.markdown("###")
                with st.container(border=True):
                    if os.path.exists(game.image_url):
                        st.image(game.image_url, width=150)
                    else:
                        st.image("https://via.placeholder.com/150", width=150)
                    st.markdown(f"**{game.nama}**")
                    st.markdown(f"`{rp(game.harga)}/jam`")

                    if st.button(f"Mainkan", key=f"play_{game.id}"):
                        with st.expander(f"\U0001F579️ Mainkan {game.nama}", expanded=True):
                            st.markdown(f"**Harga per jam:** {rp(game.harga)}")
                            jam = st.number_input("Jumlah Jam", min_value=1, step=1, key=f"jam_{game.id}")
                            total = jam * game.harga
                            st.markdown(f"**Total Harga:** {rp(total)}")
                            if st.button("\u2705 Konfirmasi", key=f"confirm_{game.id}"):
                                st.success(f"{game.nama} dipilih selama {jam} jam (Total {rp(total)}).")


# ---------- Pelanggan ----------
elif menu == "Pelanggan":
    st.header("Daftar Pelanggan")
    with st.form("form_pelanggan", clear_on_submit=True):
        nama = st.text_input("Nama Pelanggan*")
        nomor = st.text_input("Nomor HP/ID*")
        if st.form_submit_button("Tambah"):
            if nama and nomor:
                ok = m.tambah_pelanggan(nama, nomor)
                st.success("✅ Ditambahkan.") if ok else st.error("❌ Gagal.")
            else:
                st.warning("Nama & Nomor wajib.")

    df = pd.DataFrame([p.__dict__ for p in m.semua_pelanggan()])
    if not df.empty:
        st.dataframe(df.rename(columns={"id": "ID"}), use_container_width=True, hide_index=True)

# ---------- Transaksi ----------
elif menu == "Transaksi":
    st.header("Catat Transaksi")
    pelanggan = m.semua_pelanggan()
    game = m.semua_game()
    if not pelanggan or not game:
        st.info("Tambahkan pelanggan & game dulu.")
    else:
        with st.form("form_tx", clear_on_submit=True):
            pel_opt = {f"{p.nama} ({p.nomor})": p.id for p in pelanggan}
            game_opt = {f"{g.nama} – {rp(g.harga)}": g.id for g in game}
            id_pel = pel_opt[st.selectbox("Pelanggan*", list(pel_opt.keys()))]
            id_game = game_opt[st.selectbox("Game*", list(game_opt.keys()))]
            jumlah = st.number_input("Jumlah Main*", min_value=1, step=1, value=1)
            tanggal = st.date_input("Tanggal*", value=datetime.date.today())
            if st.form_submit_button("Simpan"):
                ok = m.tambah_transaksi(id_pel, id_game, jumlah, tanggal)
                st.success("✅ Tersimpan.") if ok else st.error("❌ Gagal.")

# ---------- Riwayat ----------
elif menu == "Riwayat":
    st.header("Riwayat Transaksi")
    df = m.df_transaksi()
    if df.empty:
        st.info("Belum ada data.")
    else:
        df["harga"] = df["harga"].map(rp)
        df["total"] = df["total"].map(rp)
        st.dataframe(df.rename(columns={
            "pelanggan": "Pelanggan", "nomor": "Nomor",
            "game": "Game", "harga": "Harga", "jumlah": "Qty",
            "total": "Total", "tanggal": "Tanggal"
        }), use_container_width=True, hide_index=True)

# ---------- Ringkasan ----------
elif menu == "Ringkasan":
    st.header("Ringkasan Pengeluaran Harian")
    pilihan = st.selectbox("Filter", ["Semua", "Hari Ini", "Pilih Tanggal"])
    tgl = None
    if pilihan == "Hari Ini":
        tgl = datetime.date.today()
    elif pilihan == "Pilih Tanggal":
        tgl = st.date_input("Tanggal", value=datetime.date.today())

    total = m.total_harian(tgl)
    st.metric("Total Pengeluaran", rp(total))

    st.subheader("Tot per Game")
    per_game = m.total_per_game(tgl)
    if not per_game:
        st.info("Tidak ada data.")
    else:
        df = pd.DataFrame({"Game": list(per_game.keys()), "Total": [rp(v) for v in per_game.values()]})
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.bar_chart(pd.Series(per_game))
