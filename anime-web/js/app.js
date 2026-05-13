/**
 * AniStream — Movie Recommender CLI (Web Version)
 * Menggunakan Jikan API v4 (https://api.jikan.moe/v4)
 * Tidak perlu API key, gratis & legal.
 */

// ===== CONFIG =====
const API_BASE = "https://api.jikan.moe/v4";
const RATE_LIMIT_MS = 400; // Jikan rate limit ~3 req/sec

// ===== STATE =====
let currentPage = "home";
let lastRequestTime = 0;

// ===== DOM ELEMENTS =====
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const elements = {
    // Navbar
    searchInput: $("#searchInput"),
    searchBtn: $("#searchBtn"),
    mobileMenuBtn: $("#mobileMenuBtn"),
    navLinks: $(".nav-links"),

    // Hero
    heroSection: $("#heroSection"),
    heroTitle: $("#heroTitle"),
    heroDesc: $("#heroDesc"),
    heroWatchBtn: $("#heroWatchBtn"),
    heroInfoBtn: $("#heroInfoBtn"),

    // Sections
    sectionHome: $("#sectionHome"),
    sectionTrending: $("#sectionTrending"),
    sectionGenre: $("#sectionGenre"),
    sectionSchedule: $("#sectionSchedule"),
    sectionTitle: $("#sectionTitle"),

    // Grids
    animeGrid: $("#animeGrid"),
    trendingGrid: $("#trendingGrid"),
    genreGrid: $("#genreGrid"),
    scheduleGrid: $("#scheduleGrid"),
    genreList: $("#genreList"),
    scheduleTabs: $("#scheduleTabs"),

    // Loading
    loading: $("#loading"),

    // Modal
    modalOverlay: $("#modalOverlay"),
    detailModal: $("#detailModal"),
    modalClose: $("#modalClose"),
    modalBanner: $("#modalBanner"),
    modalTitle: $("#modalTitle"),
    modalMeta: $("#modalMeta"),
    modalGenres: $("#modalGenres"),
    modalSynopsis: $("#modalSynopsis"),
    modalInfoGrid: $("#modalInfoGrid"),
    modalTrailer: $("#modalTrailer"),
};

// ===== API HELPERS =====

async function rateLimitedFetch(url) {
    const now = Date.now();
    const elapsed = now - lastRequestTime;
    if (elapsed < RATE_LIMIT_MS) {
        await sleep(RATE_LIMIT_MS - elapsed);
    }
    lastRequestTime = Date.now();

    const response = await fetch(url);
    if (!response.ok) {
        if (response.status === 429) {
            // Rate limited — wait and retry
            await sleep(1500);
            return rateLimitedFetch(url);
        }
        throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

// ===== API FUNCTIONS =====

async function fetchSeasonNow() {
    const data = await rateLimitedFetch(`${API_BASE}/seasons/now?limit=24`);
    return data.data || [];
}

async function fetchTopAnime() {
    const data = await rateLimitedFetch(`${API_BASE}/top/anime?limit=24`);
    return data.data || [];
}

async function fetchSearchAnime(query) {
    const data = await rateLimitedFetch(
        `${API_BASE}/anime?q=${encodeURIComponent(query)}&limit=24&sfw=true`
    );
    return data.data || [];
}

async function fetchAnimeDetail(malId) {
    const data = await rateLimitedFetch(`${API_BASE}/anime/${malId}/full`);
    return data.data || null;
}

async function fetchAnimeGenres() {
    const data = await rateLimitedFetch(`${API_BASE}/genres/anime`);
    return data.data || [];
}

async function fetchAnimeByGenre(genreId) {
    const data = await rateLimitedFetch(
        `${API_BASE}/anime?genres=${genreId}&limit=24&order_by=score&sort=desc&sfw=true`
    );
    return data.data || [];
}

async function fetchSchedule(day) {
    const data = await rateLimitedFetch(`${API_BASE}/schedules?filter=${day}&limit=24`);
    return data.data || [];
}

async function fetchRecommendations(malId) {
    const data = await rateLimitedFetch(`${API_BASE}/anime/${malId}/recommendations`);
    return data.data || [];
}

// ===== RENDER FUNCTIONS =====

function createAnimeCard(anime) {
    const card = document.createElement("div");
    card.className = "anime-card";
    card.dataset.id = anime.mal_id;

    const imageUrl =
        anime.images?.jpg?.large_image_url ||
        anime.images?.jpg?.image_url ||
        "";
    const score = anime.score ? anime.score.toFixed(1) : "N/A";
    const type = anime.type || "";
    const episodes = anime.episodes ? `${anime.episodes} ep` : "Ongoing";
    const year = anime.year || (anime.aired?.prop?.from?.year) || "";

    card.innerHTML = `
        <div class="card-image">
            <img src="${imageUrl}" alt="${anime.title}" loading="lazy" 
                 onerror="this.src='https://via.placeholder.com/300x400/1a1a2e/6b6b80?text=No+Image'">
            ${type ? `<span class="card-badge">${type}</span>` : ""}
            <span class="card-score">⭐ ${score}</span>
        </div>
        <div class="card-info">
            <h3 class="card-title">${anime.title}</h3>
            <div class="card-meta">
                <span>${episodes}</span>
                ${year ? `<span>${year}</span>` : ""}
            </div>
        </div>
    `;

    card.addEventListener("click", () => openDetail(anime.mal_id));
    return card;
}

function renderGrid(container, animeList) {
    container.innerHTML = "";
    if (!animeList || animeList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="emoji">🔍</div>
                <p>Tidak ada anime ditemukan.</p>
            </div>
        `;
        return;
    }
    animeList.forEach((anime) => {
        container.appendChild(createAnimeCard(anime));
    });
}

function showLoading(show) {
    if (show) {
        elements.loading.classList.remove("hidden");
    } else {
        elements.loading.classList.add("hidden");
    }
}

// ===== HERO =====

let heroAnime = null;

async function setupHero(animeList) {
    if (!animeList || animeList.length === 0) return;

    // Pick a random popular one for hero
    const top5 = animeList.slice(0, 5);
    heroAnime = top5[Math.floor(Math.random() * top5.length)];

    const bannerUrl =
        heroAnime.images?.jpg?.large_image_url ||
        heroAnime.images?.jpg?.image_url ||
        "";

    elements.heroSection.style.backgroundImage = `url(${bannerUrl})`;
    elements.heroSection.style.backgroundSize = "cover";
    elements.heroSection.style.backgroundPosition = "center";
    elements.heroTitle.textContent = heroAnime.title;
    elements.heroDesc.textContent =
        heroAnime.synopsis
            ? heroAnime.synopsis.substring(0, 200) + "..."
            : "Anime populer musim ini.";
}

// ===== DETAIL MODAL =====

async function openDetail(malId) {
    elements.modalOverlay.classList.remove("hidden");
    document.body.style.overflow = "hidden";

    // Reset
    elements.modalBanner.style.backgroundImage = "";
    elements.modalTitle.textContent = "Memuat...";
    elements.modalMeta.innerHTML = "";
    elements.modalGenres.innerHTML = "";
    elements.modalSynopsis.textContent = "";
    elements.modalInfoGrid.innerHTML = "";
    elements.modalTrailer.innerHTML = "";

    try {
        const anime = await fetchAnimeDetail(malId);
        if (!anime) {
            elements.modalTitle.textContent = "Data tidak ditemukan.";
            return;
        }

        const bannerUrl =
            anime.images?.jpg?.large_image_url ||
            anime.images?.jpg?.image_url ||
            "";

        elements.modalBanner.style.backgroundImage = `url(${bannerUrl})`;

        elements.modalTitle.textContent =
            anime.title_english || anime.title || "?";

        // Meta
        const score = anime.score ? `⭐ ${anime.score}/10` : "";
        const episodes = anime.episodes ? `📺 ${anime.episodes} episode` : "Ongoing";
        const duration = anime.duration || "";
        const status = anime.status || "";
        const season = anime.season
            ? `${capitalize(anime.season)} ${anime.year || ""}`
            : "";

        elements.modalMeta.innerHTML = [score, episodes, duration, status, season]
            .filter(Boolean)
            .map((s) => `<span>${s}</span>`)
            .join("");

        // Genres
        const genres = anime.genres || [];
        elements.modalGenres.innerHTML = genres
            .map((g) => `<span>${g.name}</span>`)
            .join("");

        // Synopsis
        elements.modalSynopsis.textContent =
            anime.synopsis || "Tidak ada sinopsis.";

        // Info grid
        const infoItems = [
            { label: "Studio", value: (anime.studios || []).map((s) => s.name).join(", ") || "-" },
            { label: "Sumber", value: anime.source || "-" },
            { label: "Rating", value: anime.rating || "-" },
            { label: "Peringkat", value: anime.rank ? `#${anime.rank}` : "-" },
            { label: "Popularitas", value: anime.popularity ? `#${anime.popularity}` : "-" },
            { label: "Member", value: anime.members ? anime.members.toLocaleString() : "-" },
        ];

        elements.modalInfoGrid.innerHTML = infoItems
            .map(
                (item) => `
                <div class="modal-info-item">
                    <div class="label">${item.label}</div>
                    <div class="value">${item.value}</div>
                </div>
            `
            )
            .join("");

        // Trailer
        if (anime.trailer?.embed_url) {
            elements.modalTrailer.innerHTML = `
                <iframe src="${anime.trailer.embed_url}" 
                        allowfullscreen
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
                </iframe>
            `;
        } else {
            elements.modalTrailer.innerHTML = `
                <p style="color: var(--text-muted); font-size: 0.85rem;">Trailer tidak tersedia.</p>
            `;
        }
    } catch (err) {
        console.error("Error fetching detail:", err);
        elements.modalTitle.textContent = "Gagal memuat data.";
    }
}

function closeModal() {
    elements.modalOverlay.classList.add("hidden");
    document.body.style.overflow = "";
    elements.modalTrailer.innerHTML = ""; // Stop video
}

// ===== NAVIGATION =====

function switchPage(page) {
    currentPage = page;

    // Hide all sections
    [
        elements.sectionHome,
        elements.sectionTrending,
        elements.sectionGenre,
        elements.sectionSchedule,
    ].forEach((s) => s.classList.add("hidden"));

    // Update nav
    $$(".nav-links a").forEach((a) => a.classList.remove("active"));
    const activeLink = $(`.nav-links a[data-page="${page}"]`);
    if (activeLink) activeLink.classList.add("active");

    // Show section
    switch (page) {
        case "home":
            elements.sectionHome.classList.remove("hidden");
            elements.heroSection.classList.remove("hidden");
            loadHome();
            break;
        case "trending":
            elements.sectionTrending.classList.remove("hidden");
            elements.heroSection.classList.add("hidden");
            loadTrending();
            break;
        case "genre":
            elements.sectionGenre.classList.remove("hidden");
            elements.heroSection.classList.add("hidden");
            loadGenres();
            break;
        case "schedule":
            elements.sectionSchedule.classList.remove("hidden");
            elements.heroSection.classList.add("hidden");
            loadSchedule();
            break;
    }
}

// ===== PAGE LOADERS =====

let homeLoaded = false;
let trendingLoaded = false;
let genresLoaded = false;
let scheduleLoaded = false;

async function loadHome() {
    if (homeLoaded) return;
    showLoading(true);
    try {
        const animeList = await fetchSeasonNow();
        renderGrid(elements.animeGrid, animeList);
        setupHero(animeList);
        homeLoaded = true;
        elements.sectionTitle.textContent = "🔥 Anime Populer Musim Ini";
    } catch (err) {
        console.error("Error loading home:", err);
        elements.animeGrid.innerHTML = `
            <div class="empty-state">
                <div class="emoji">😵</div>
                <p>Gagal memuat data. Coba lagi nanti.</p>
            </div>
        `;
    }
    showLoading(false);
}

async function loadTrending() {
    if (trendingLoaded) return;
    elements.trendingGrid.innerHTML = `
        <div class="loading"><div class="spinner"></div><p>Memuat...</p></div>
    `;
    try {
        const animeList = await fetchTopAnime();
        renderGrid(elements.trendingGrid, animeList);
        trendingLoaded = true;
    } catch (err) {
        console.error("Error loading trending:", err);
        elements.trendingGrid.innerHTML = `
            <div class="empty-state"><div class="emoji">😵</div><p>Gagal memuat.</p></div>
        `;
    }
}

async function loadGenres() {
    if (genresLoaded) return;
    elements.genreList.innerHTML = `<div class="loading"><div class="spinner"></div></div>`;
    try {
        const genres = await fetchAnimeGenres();
        elements.genreList.innerHTML = "";
        genres.slice(0, 30).forEach((genre) => {
            const tag = document.createElement("button");
            tag.className = "genre-tag";
            tag.textContent = genre.name;
            tag.dataset.id = genre.mal_id;
            tag.addEventListener("click", () => selectGenre(genre.mal_id, genre.name));
            elements.genreList.appendChild(tag);
        });
        genresLoaded = true;
    } catch (err) {
        console.error("Error loading genres:", err);
        elements.genreList.innerHTML = `<p style="color:var(--text-muted)">Gagal memuat genre.</p>`;
    }
}

async function selectGenre(genreId, genreName) {
    // Update active tag
    $$(".genre-tag").forEach((t) => t.classList.remove("active"));
    const activeTag = $(`.genre-tag[data-id="${genreId}"]`);
    if (activeTag) activeTag.classList.add("active");

    elements.genreGrid.innerHTML = `
        <div class="loading"><div class="spinner"></div><p>Memuat anime ${genreName}...</p></div>
    `;
    try {
        const animeList = await fetchAnimeByGenre(genreId);
        renderGrid(elements.genreGrid, animeList);
    } catch (err) {
        console.error("Error fetching genre:", err);
        elements.genreGrid.innerHTML = `
            <div class="empty-state"><div class="emoji">😵</div><p>Gagal memuat.</p></div>
        `;
    }
}

const DAYS = [
    { key: "monday", label: "Senin" },
    { key: "tuesday", label: "Selasa" },
    { key: "wednesday", label: "Rabu" },
    { key: "thursday", label: "Kamis" },
    { key: "friday", label: "Jumat" },
    { key: "saturday", label: "Sabtu" },
    { key: "sunday", label: "Minggu" },
];

async function loadSchedule() {
    if (scheduleLoaded) return;

    // Render day tabs
    elements.scheduleTabs.innerHTML = "";
    DAYS.forEach((day, idx) => {
        const tab = document.createElement("button");
        tab.className = "schedule-tab" + (idx === 0 ? " active" : "");
        tab.textContent = day.label;
        tab.dataset.day = day.key;
        tab.addEventListener("click", () => selectDay(day.key));
        elements.scheduleTabs.appendChild(tab);
    });

    // Load today (or Monday as default)
    const todayIdx = new Date().getDay(); // 0=Sun
    const mappedDay = todayIdx === 0 ? "sunday" : DAYS[todayIdx - 1].key;
    await selectDay(mappedDay);
    scheduleLoaded = true;
}

async function selectDay(day) {
    $$(".schedule-tab").forEach((t) => t.classList.remove("active"));
    const activeTab = $(`.schedule-tab[data-day="${day}"]`);
    if (activeTab) activeTab.classList.add("active");

    elements.scheduleGrid.innerHTML = `
        <div class="loading"><div class="spinner"></div><p>Memuat jadwal...</p></div>
    `;
    try {
        const animeList = await fetchSchedule(day);
        renderGrid(elements.scheduleGrid, animeList);
    } catch (err) {
        console.error("Error loading schedule:", err);
        elements.scheduleGrid.innerHTML = `
            <div class="empty-state"><div class="emoji">😵</div><p>Gagal memuat.</p></div>
        `;
    }
}

// ===== SEARCH =====

async function performSearch(query) {
    if (!query.trim()) return;

    switchPage("home");
    homeLoaded = true; // prevent reload
    elements.heroSection.classList.add("hidden");
    elements.sectionTitle.textContent = `🔍 Hasil pencarian: "${query}"`;
    showLoading(true);
    elements.animeGrid.innerHTML = "";

    try {
        const results = await fetchSearchAnime(query);
        renderGrid(elements.animeGrid, results);
    } catch (err) {
        console.error("Search error:", err);
        elements.animeGrid.innerHTML = `
            <div class="empty-state"><div class="emoji">😵</div><p>Gagal mencari.</p></div>
        `;
    }
    showLoading(false);
}

// ===== UTILITY =====

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ===== EVENT LISTENERS =====

function initEvents() {
    // Navigation
    $$(".nav-links a").forEach((link) => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) switchPage(page);
            // Close mobile menu
            elements.navLinks.classList.remove("show");
        });
    });

    // Mobile menu
    elements.mobileMenuBtn.addEventListener("click", () => {
        elements.navLinks.classList.toggle("show");
    });

    // Search
    elements.searchBtn.addEventListener("click", () => {
        performSearch(elements.searchInput.value);
    });

    elements.searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            performSearch(elements.searchInput.value);
        }
    });

    // Modal close
    elements.modalClose.addEventListener("click", closeModal);
    elements.modalOverlay.addEventListener("click", (e) => {
        if (e.target === elements.modalOverlay) closeModal();
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeModal();
    });

    // Hero buttons
    elements.heroWatchBtn.addEventListener("click", () => {
        if (heroAnime) openDetail(heroAnime.mal_id);
    });
    elements.heroInfoBtn.addEventListener("click", () => {
        if (heroAnime) openDetail(heroAnime.mal_id);
    });
}

// ===== INIT =====

document.addEventListener("DOMContentLoaded", () => {
    initEvents();
    switchPage("home");
});
