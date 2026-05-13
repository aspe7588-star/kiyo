#!/usr/bin/env python3
"""
Movie Recommender CLI (movie_rec)
---------------------------------
CLI interaktif untuk mencari film, mendapat rekomendasi,
mengelola watchlist, dan memberi rating — didukung oleh TMDB API.

Fitur:
  - Cari film berdasarkan judul
  - Lihat detail film (sinopsis, rating, genre, tahun rilis)
  - Dapatkan rekomendasi berdasarkan film tertentu
  - Film populer & trending minggu ini
  - Kelola watchlist lokal
  - Beri rating film dan lihat histori rating

Persyaratan:
  - Python 3.8+
  - TMDB API Key (gratis, daftar di https://www.themoviedb.org/settings/api)
  - Koneksi internet

Penggunaan:
    python movie_rec.py                # menu interaktif
    python movie_rec.py search "Inception"
    python movie_rec.py trending
    python movie_rec.py popular
    python movie_rec.py recommend 550
    python movie_rec.py watchlist
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.request
import urllib.error
import urllib.parse
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------

DATA_DIR = Path.home() / ".movie_rec"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
RATINGS_FILE = DATA_DIR / "ratings.json"
CONFIG_FILE = DATA_DIR / "config.json"

TMDB_BASE = "https://api.themoviedb.org/3"

# ---------------------------------------------------------------------------
# Helpers — TMDB API
# ---------------------------------------------------------------------------


def get_api_key() -> str:
    """Ambil API key dari config, env variable, atau minta ke user."""
    # 1. Cek environment variable
    key = os.environ.get("TMDB_API_KEY", "")
    if key:
        return key

    # 2. Cek config file
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if cfg.get("api_key"):
                return cfg["api_key"]
        except (json.JSONDecodeError, KeyError):
            pass

    # 3. Minta input
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║  TMDB API Key belum disetting.                      ║")
    print("║  Daftar gratis: https://www.themoviedb.org/settings/api ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    key = input("Masukkan TMDB API Key: ").strip()
    if not key:
        print("API key diperlukan. Keluar.")
        sys.exit(1)

    # Simpan
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"api_key": key}, indent=2), encoding="utf-8")
    print("API key tersimpan di ~/.movie_rec/config.json\n")
    return key


def tmdb_get(endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """HTTP GET request ke TMDB API."""
    api_key = get_api_key()
    if params is None:
        params = {}
    params["api_key"] = api_key
    params.setdefault("language", "id-ID")  # Bahasa Indonesia

    url = f"{TMDB_BASE}{endpoint}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("\n[ERROR] API key tidak valid. Periksa kembali key kamu.")
            print("Hapus file ~/.movie_rec/config.json lalu coba lagi.\n")
        elif e.code == 404:
            print("\n[ERROR] Data tidak ditemukan.\n")
        else:
            print(f"\n[ERROR] HTTP {e.code}: {e.reason}\n")
        return {}
    except urllib.error.URLError as e:
        print(f"\n[ERROR] Gagal terhubung ke TMDB: {e.reason}")
        print("Pastikan koneksi internet tersedia.\n")
        return {}


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

STAR = "★"
STAR_EMPTY = "☆"


def star_rating(score: float, max_stars: int = 5) -> str:
    """Konversi skor 0-10 ke bintang."""
    filled = round(score / 10 * max_stars)
    return STAR * filled + STAR_EMPTY * (max_stars - filled)


def fmt_movie_short(m: Dict[str, Any], idx: int = 0) -> str:
    """Format satu baris ringkas film."""
    title = m.get("title") or m.get("name") or "?"
    year = (m.get("release_date") or m.get("first_air_date") or "")[:4]
    vote = m.get("vote_average", 0)
    movie_id = m.get("id", "")
    year_str = f"({year})" if year else ""
    prefix = f"  {idx:>2}. " if idx else "  • "
    return f"{prefix}[{movie_id}] {title} {year_str}  {star_rating(vote)} {vote:.1f}/10"


def fmt_movie_detail(m: Dict[str, Any]) -> str:
    """Format detail lengkap film."""
    title = m.get("title") or m.get("name") or "?"
    original = m.get("original_title") or ""
    year = (m.get("release_date") or "")[:4]
    runtime = m.get("runtime", 0)
    genres = ", ".join(g["name"] for g in m.get("genres", []))
    vote = m.get("vote_average", 0)
    vote_count = m.get("vote_count", 0)
    overview = m.get("overview") or "(tidak ada sinopsis)"
    tagline = m.get("tagline") or ""
    status = m.get("status") or ""

    lines = [
        "=" * 60,
        f"  {title} ({year})" if year else f"  {title}",
    ]
    if original and original != title:
        lines.append(f"  Judul asli: {original}")
    if tagline:
        lines.append(f"  \"{tagline}\"")
    lines.append("=" * 60)
    lines.append(f"  ID       : {m.get('id')}")
    lines.append(f"  Genre    : {genres}")
    lines.append(f"  Durasi   : {runtime} menit" if runtime else "")
    lines.append(f"  Status   : {status}" if status else "")
    lines.append(f"  Rating   : {star_rating(vote)} {vote:.1f}/10 ({vote_count:,} votes)")
    lines.append("")
    lines.append("  Sinopsis:")
    for line in textwrap.wrap(overview, width=56):
        lines.append(f"    {line}")
    lines.append("")
    return "\n".join(l for l in lines if l is not None)


# ---------------------------------------------------------------------------
# Local Storage (Watchlist & Ratings)
# ---------------------------------------------------------------------------

class LocalStore:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write([])

    def _read(self) -> List[Dict]:
        try:
            return json.loads(self.filepath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write(self, data: List[Dict]) -> None:
        self.filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def all(self) -> List[Dict]:
        return self._read()

    def add(self, item: Dict) -> None:
        rows = self._read()
        rows.append(item)
        self._write(rows)

    def remove_by_id(self, movie_id: int) -> bool:
        rows = self._read()
        new = [r for r in rows if r.get("id") != movie_id]
        if len(new) == len(rows):
            return False
        self._write(new)
        return True

    def find_by_id(self, movie_id: int) -> Optional[Dict]:
        return next((r for r in self._read() if r.get("id") == movie_id), None)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_search(args=None) -> None:
    """Cari film berdasarkan judul."""
    if args and args.query:
        query = " ".join(args.query)
    else:
        query = input("\nMasukkan judul film: ").strip()
    if not query:
        print("Query kosong.")
        return

    data = tmdb_get("/search/movie", {"query": query})
    results = data.get("results", [])
    if not results:
        print(f"\nTidak ditemukan hasil untuk '{query}'.\n")
        return

    print(f"\n  Hasil pencarian: \"{query}\" ({len(results)} film)\n")
    for i, m in enumerate(results[:15], 1):
        print(fmt_movie_short(m, i))
    print()
    print("  Gunakan 'detail <id>' untuk info lengkap.")
    print()


def cmd_detail(args=None) -> None:
    """Lihat detail film."""
    if args and args.movie_id:
        movie_id = args.movie_id
    else:
        raw = input("\nMasukkan ID film: ").strip()
        try:
            movie_id = int(raw)
        except ValueError:
            print("ID harus angka.")
            return

    data = tmdb_get(f"/movie/{movie_id}")
    if not data:
        return
    print()
    print(fmt_movie_detail(data))


def cmd_recommend(args=None) -> None:
    """Dapatkan rekomendasi berdasarkan film tertentu."""
    if args and args.movie_id:
        movie_id = args.movie_id
    else:
        raw = input("\nMasukkan ID film basis rekomendasi: ").strip()
        try:
            movie_id = int(raw)
        except ValueError:
            print("ID harus angka.")
            return

    # Ambil judul film basis
    base = tmdb_get(f"/movie/{movie_id}")
    base_title = base.get("title", f"ID {movie_id}")

    data = tmdb_get(f"/movie/{movie_id}/recommendations")
    results = data.get("results", [])
    if not results:
        print(f"\nTidak ada rekomendasi untuk '{base_title}'.\n")
        return

    print(f"\n  Rekomendasi berdasarkan \"{base_title}\":\n")
    for i, m in enumerate(results[:15], 1):
        print(fmt_movie_short(m, i))
    print()


def cmd_trending(args=None) -> None:
    """Film trending minggu ini."""
    data = tmdb_get("/trending/movie/week")
    results = data.get("results", [])
    if not results:
        print("\nTidak ada data trending.\n")
        return

    print("\n  🔥 Trending Minggu Ini:\n")
    for i, m in enumerate(results[:15], 1):
        print(fmt_movie_short(m, i))
    print()


def cmd_popular(args=None) -> None:
    """Film populer saat ini."""
    data = tmdb_get("/movie/popular")
    results = data.get("results", [])
    if not results:
        print("\nTidak ada data.\n")
        return

    print("\n  🎬 Film Populer:\n")
    for i, m in enumerate(results[:15], 1):
        print(fmt_movie_short(m, i))
    print()


def cmd_discover(args=None) -> None:
    """Discover film berdasarkan genre."""
    # Genre list
    genres_data = tmdb_get("/genre/movie/list")
    genres = genres_data.get("genres", [])
    if not genres:
        print("Gagal mengambil daftar genre.")
        return

    print("\n  Pilih genre:\n")
    for i, g in enumerate(genres, 1):
        print(f"    {i:>2}. {g['name']}")
    print()

    raw = input("  Nomor genre: ").strip()
    try:
        idx = int(raw) - 1
        genre_id = genres[idx]["id"]
        genre_name = genres[idx]["name"]
    except (ValueError, IndexError):
        print("  Pilihan tidak valid.")
        return

    data = tmdb_get("/discover/movie", {
        "with_genres": str(genre_id),
        "sort_by": "vote_average.desc",
        "vote_count.gte": "100",
    })
    results = data.get("results", [])
    if not results:
        print(f"\nTidak ada film untuk genre '{genre_name}'.\n")
        return

    print(f"\n  Film genre \"{genre_name}\" (rating tertinggi):\n")
    for i, m in enumerate(results[:15], 1):
        print(fmt_movie_short(m, i))
    print()


# --- Watchlist ---

def cmd_watchlist(args=None) -> None:
    """Kelola watchlist."""
    store = LocalStore(WATCHLIST_FILE)
    items = store.all()
    if not items:
        print("\n  Watchlist kosong. Tambah film dengan 'watchlist add <id>'.\n")
        return

    print(f"\n  📋 Watchlist kamu ({len(items)} film):\n")
    for i, m in enumerate(items, 1):
        title = m.get("title", "?")
        year = m.get("year", "")
        mid = m.get("id", "")
        added = m.get("added_at", "")[:10]
        print(f"    {i:>2}. [{mid}] {title} ({year})  — ditambahkan {added}")
    print()


def cmd_watchlist_add(args=None) -> None:
    """Tambah film ke watchlist."""
    if args and args.movie_id:
        movie_id = args.movie_id
    else:
        raw = input("\nMasukkan ID film: ").strip()
        try:
            movie_id = int(raw)
        except ValueError:
            print("ID harus angka.")
            return

    store = LocalStore(WATCHLIST_FILE)
    if store.find_by_id(movie_id):
        print("Film sudah ada di watchlist.")
        return

    data = tmdb_get(f"/movie/{movie_id}")
    if not data:
        return

    entry = {
        "id": data["id"],
        "title": data.get("title", "?"),
        "year": (data.get("release_date") or "")[:4],
        "added_at": datetime.now().isoformat(),
    }
    store.add(entry)
    print(f"\n  ✅ '{entry['title']}' ditambahkan ke watchlist.\n")


def cmd_watchlist_remove(args=None) -> None:
    """Hapus film dari watchlist."""
    if args and args.movie_id:
        movie_id = args.movie_id
    else:
        raw = input("\nMasukkan ID film: ").strip()
        try:
            movie_id = int(raw)
        except ValueError:
            print("ID harus angka.")
            return

    store = LocalStore(WATCHLIST_FILE)
    if store.remove_by_id(movie_id):
        print("  ✅ Dihapus dari watchlist.")
    else:
        print("  Film tidak ditemukan di watchlist.")


# --- Ratings ---

def cmd_rate(args=None) -> None:
    """Beri rating film (1-10)."""
    if args and args.movie_id:
        movie_id = args.movie_id
    else:
        raw = input("\nMasukkan ID film: ").strip()
        try:
            movie_id = int(raw)
        except ValueError:
            print("ID harus angka.")
            return

    # Ambil info film
    data = tmdb_get(f"/movie/{movie_id}")
    if not data:
        return
    title = data.get("title", "?")

    while True:
        score_raw = input(f"  Rating untuk '{title}' (1-10): ").strip()
        try:
            score = int(score_raw)
            if 1 <= score <= 10:
                break
        except ValueError:
            pass
        print("  Rating harus angka 1-10.")

    store = LocalStore(RATINGS_FILE)
    # Hapus rating lama jika ada
    store.remove_by_id(movie_id)
    entry = {
        "id": movie_id,
        "title": title,
        "year": (data.get("release_date") or "")[:4],
        "score": score,
        "rated_at": datetime.now().isoformat(),
    }
    store.add(entry)
    print(f"\n  ✅ '{title}' diberi rating {STAR * score}{STAR_EMPTY * (10 - score)} ({score}/10)\n")


def cmd_my_ratings(args=None) -> None:
    """Lihat histori rating."""
    store = LocalStore(RATINGS_FILE)
    items = store.all()
    if not items:
        print("\n  Belum ada rating. Gunakan 'rate <id>' untuk memberi rating.\n")
        return

    items.sort(key=lambda x: x.get("rated_at", ""), reverse=True)
    print(f"\n  ⭐ Rating kamu ({len(items)} film):\n")
    for i, m in enumerate(items, 1):
        title = m.get("title", "?")
        year = m.get("year", "")
        score = m.get("score", 0)
        print(f"    {i:>2}. [{m['id']}] {title} ({year})  {STAR * score}{STAR_EMPTY * (10 - score)} {score}/10")
    print()


# ---------------------------------------------------------------------------
# Mode interaktif
# ---------------------------------------------------------------------------

MENU = """
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
"""

ACTIONS = {
    "1": cmd_search,
    "2": cmd_detail,
    "3": cmd_recommend,
    "4": cmd_trending,
    "5": cmd_popular,
    "6": cmd_discover,
    "7": cmd_watchlist,
    "8": cmd_watchlist_add,
    "9": cmd_watchlist_remove,
    "10": cmd_rate,
    "11": cmd_my_ratings,
}


def interactive() -> None:
    while True:
        print(MENU)
        choice = input("  Pilih menu: ").strip()
        if choice in ("0", "q", "quit", "exit"):
            print("\n  Sampai jumpa! 🍿\n")
            return
        action = ACTIONS.get(choice)
        if not action:
            print("  Pilihan tidak valid.")
            continue
        try:
            action()
        except (KeyboardInterrupt, EOFError):
            print("\n  (dibatalkan)")


# ---------------------------------------------------------------------------
# CLI Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="movie_rec",
        description="CLI Movie Recommender — didukung oleh TMDB API.",
    )
    sub = p.add_subparsers(dest="command")

    # search
    p_search = sub.add_parser("search", help="Cari film berdasarkan judul")
    p_search.add_argument("query", nargs="*", help="Judul film")

    # detail
    p_detail = sub.add_parser("detail", help="Detail film")
    p_detail.add_argument("movie_id", type=int, help="TMDB movie ID")

    # recommend
    p_rec = sub.add_parser("recommend", help="Rekomendasi berdasarkan film")
    p_rec.add_argument("movie_id", type=int, help="TMDB movie ID")

    # trending
    sub.add_parser("trending", help="Film trending minggu ini")

    # popular
    sub.add_parser("popular", help="Film populer saat ini")

    # discover
    sub.add_parser("discover", help="Discover film berdasarkan genre")

    # watchlist
    sub.add_parser("watchlist", help="Lihat watchlist")

    # watchlist-add
    p_wa = sub.add_parser("watchlist-add", help="Tambah film ke watchlist")
    p_wa.add_argument("movie_id", type=int, help="TMDB movie ID")

    # watchlist-remove
    p_wr = sub.add_parser("watchlist-remove", help="Hapus film dari watchlist")
    p_wr.add_argument("movie_id", type=int, help="TMDB movie ID")

    # rate
    p_rate = sub.add_parser("rate", help="Beri rating film")
    p_rate.add_argument("movie_id", type=int, help="TMDB movie ID")

    # my-ratings
    sub.add_parser("my-ratings", help="Lihat histori rating")

    return p


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "search": cmd_search,
        "detail": cmd_detail,
        "recommend": cmd_recommend,
        "trending": cmd_trending,
        "popular": cmd_popular,
        "discover": cmd_discover,
        "watchlist": cmd_watchlist,
        "watchlist-add": cmd_watchlist_add,
        "watchlist-remove": cmd_watchlist_remove,
        "rate": cmd_rate,
        "my-ratings": cmd_my_ratings,
    }

    try:
        if args.command is None:
            interactive()
        else:
            handlers[args.command](args)
    except (KeyboardInterrupt, EOFError):
        print("\n  Dibatalkan.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
