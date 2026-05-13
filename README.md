# 🎬 Movie Recommender CLI

CLI interaktif untuk mencari film, mendapat rekomendasi, mengelola watchlist,
dan memberi rating — didukung oleh [TMDB API](https://www.themoviedb.org/) (gratis & legal).

---

## Fitur

| # | Fitur | Keterangan |
|---|-------|------------|
| 1 | **Cari film** | Cari berdasarkan judul, tampilkan rating & tahun |
| 2 | **Detail film** | Sinopsis, genre, durasi, rating TMDB |
| 3 | **Rekomendasi** | Film serupa berdasarkan film yang kamu suka |
| 4 | **Trending** | Film trending minggu ini |
| 5 | **Populer** | Film populer saat ini |
| 6 | **Discover** | Temukan film berdasarkan genre favorit |
| 7 | **Watchlist** | Simpan film yang ingin ditonton (lokal) |
| 8 | **Rating** | Beri rating 1-10 dan lihat histori |

---

## Persyaratan

- **Python 3.8+** (tanpa library eksternal)
- **TMDB API Key** — daftar gratis di https://www.themoviedb.org/settings/api
- Koneksi internet

---

## Instalasi

```bash
git clone https://github.com/aspe7588-star/kiyo.git
cd kiyo
python3 movie_rec.py
```

Saat pertama kali dijalankan, kamu akan diminta memasukkan TMDB API Key.
Key tersimpan di `~/.movie_rec/config.json`.

Atau set via environment variable:

```bash
export TMDB_API_KEY="your_key_here"
python3 movie_rec.py
```

---

## Penggunaan

### Mode Interaktif

Jalankan tanpa argumen untuk menu interaktif:

```bash
python3 movie_rec.py
```

```
╔═══════════════════════════════════════════════╗
║       🎬 Movie Recommender CLI 🎬            ║
╠═══════════════════════════════════════════════╣
║  1) Cari film                                ║
║  2) Detail film                              ║
║  3) Rekomendasi berdasarkan film             ║
║  4) Film trending minggu ini                 ║
║  5) Film populer                             ║
║  6) Discover berdasarkan genre               ║
║  7) Lihat watchlist                          ║
║  8) Tambah ke watchlist                      ║
║  9) Hapus dari watchlist                     ║
║ 10) Beri rating film                         ║
║ 11) Lihat rating saya                        ║
║  0) Keluar                                   ║
╚═══════════════════════════════════════════════╝
```

### Mode CLI (Subcommands)

```bash
# Cari film
python3 movie_rec.py search "Inception"

# Detail film (pakai TMDB ID)
python3 movie_rec.py detail 27205

# Rekomendasi berdasarkan film
python3 movie_rec.py recommend 27205

# Film trending minggu ini
python3 movie_rec.py trending

# Film populer
python3 movie_rec.py popular

# Discover berdasarkan genre (interaktif pilih genre)
python3 movie_rec.py discover

# Lihat watchlist
python3 movie_rec.py watchlist

# Tambah ke watchlist
python3 movie_rec.py watchlist-add 27205

# Hapus dari watchlist
python3 movie_rec.py watchlist-remove 27205

# Beri rating
python3 movie_rec.py rate 27205

# Lihat semua rating
python3 movie_rec.py my-ratings
```

---

## Contoh Output

### Pencarian

```
  Hasil pencarian: "Inception" (5 film)

   1. [27205] Inception (2010)  ★★★★☆ 8.4/10
   2. [1982]  Inception: The Cobol Job (2010)  ★★★☆☆ 7.2/10
```

### Detail Film

```
============================================================
  Inception (2010)
  Judul asli: Inception
  "Your mind is the scene of the crime."
============================================================
  ID       : 27205
  Genre    : Action, Science Fiction, Adventure
  Durasi   : 148 menit
  Rating   : ★★★★☆ 8.4/10 (35,123 votes)

  Sinopsis:
    Cobb, a skilled thief who commits corporate espionage
    by infiltrating the subconscious of his targets...
```

### Ringkasan Rating

```
  ⭐ Rating kamu (3 film):

     1. [27205] Inception (2010)  ★★★★★★★★★☆ 9/10
     2. [550]   Fight Club (1999)  ★★★★★★★★☆☆ 8/10
     3. [680]   Pulp Fiction (1994)  ★★★★★★★★★★ 10/10
```

---

## Penyimpanan Data

Semua data lokal tersimpan di `~/.movie_rec/`:

| File | Isi |
|------|-----|
| `config.json` | API key |
| `watchlist.json` | Daftar film watchlist |
| `ratings.json` | Histori rating |

Data **tidak** di-upload atau di-share ke mana pun.

---

## File Lain di Repo Ini

- **`submgr.py`** — Streaming Account Manager: CLI untuk mencatat langganan streaming (Netflix, Spotify, dll), hitung pengeluaran bulanan/tahunan, dan pengingat tagihan.

---

## Lisensi

MIT — silakan dipakai dan dimodifikasi.

---

*Data film disediakan oleh [TMDB](https://www.themoviedb.org/). Produk ini tidak diendorse atau disertifikasi oleh TMDB.*
