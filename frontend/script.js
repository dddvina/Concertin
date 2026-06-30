/**
 * ConcertIn Frontend Application (OOP Architecture)
 * Mengelola state autentikasi, rendering konser, dan interaksi user.
 */

// ── Auth Manager (Singleton) ────────────────────────────
class AuthManager {
    static KEY = 'concertin_user';

    static getUser() {
        try {
            const raw = localStorage.getItem(AuthManager.KEY);
            return raw ? JSON.parse(raw) : null;
        } catch { return null; }
    }

    static setUser(user) {
        localStorage.setItem(AuthManager.KEY, JSON.stringify(user));
    }

    static logout() {
        localStorage.removeItem(AuthManager.KEY);
    }

    static isLoggedIn() {
        return AuthManager.getUser() !== null;
    }

    static requireAuth(redirectUrl) {
        if (!AuthManager.isLoggedIn()) {
            LoginGuardModal.show(redirectUrl);
            return false;
        }
        return true;
    }
}

// ── Toast Notification ──────────────────────────────────
class Toast {
    static container = null;

    static init() {
        if (!Toast.container) {
            Toast.container = document.createElement('div');
            Toast.container.className = 'toast-container';
            document.body.appendChild(Toast.container);
        }
    }

    static show(message, type = 'info', duration = 3500) {
        Toast.init();
        const el = document.createElement('div');
        el.className = `toast ${type}`;
        el.textContent = message;
        Toast.container.appendChild(el);
        setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, duration);
    }

    static success(msg) { Toast.show(msg, 'success'); }
    static error(msg) { Toast.show(msg, 'error'); }
    static info(msg) { Toast.show(msg, 'info'); }
}

// ── Login Guard Modal ───────────────────────────────────
class LoginGuardModal {
    static overlay = null;

    static init() {
        if (LoginGuardModal.overlay) return;
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'loginGuardModal';
        overlay.innerHTML = `
            <div class="modal">
                <i class="fas fa-lock modal-icon"></i>
                <h2>Login Diperlukan</h2>
                <p>Kamu harus masuk ke akun terlebih dahulu untuk memesan tiket konser.</p>
                <div class="modal-actions">
                    <button class="btn btn-primary" id="modalLoginBtn"><i class="fas fa-right-to-bracket"></i> Masuk</button>
                    <button class="btn btn-ghost" id="modalRegisterBtn"><i class="fas fa-user-plus"></i> Daftar</button>
                    <button class="btn btn-ghost" id="modalCloseBtn"><i class="fas fa-xmark"></i> Tutup</button>
                </div>
            </div>`;
        document.body.appendChild(overlay);
        LoginGuardModal.overlay = overlay;

        overlay.querySelector('#modalCloseBtn').addEventListener('click', () => LoginGuardModal.hide());
        overlay.querySelector('#modalLoginBtn').addEventListener('click', () => { window.location.href = 'login.html'; });
        overlay.querySelector('#modalRegisterBtn').addEventListener('click', () => { window.location.href = 'register.html'; });
        overlay.addEventListener('click', (e) => { if (e.target === overlay) LoginGuardModal.hide(); });
    }

    static show() { LoginGuardModal.init(); LoginGuardModal.overlay.classList.add('active'); }
    static hide() { if (LoginGuardModal.overlay) LoginGuardModal.overlay.classList.remove('active'); }
}

// ── API Client ──────────────────────────────────────────
class APIClient {
    static BASE = '';

    static async request(url, options = {}) {
        try {
            const res = await fetch(APIClient.BASE + url, {
                headers: { 'Content-Type': 'application/json' },
                ...options
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Terjadi kesalahan.');
            return data;
        } catch (err) {
            throw err;
        }
    }

    static get(url) { return APIClient.request(url); }
    static post(url, body) { return APIClient.request(url, { method: 'POST', body: JSON.stringify(body) }); }
}

// ── Navbar Renderer ─────────────────────────────────────
class NavbarRenderer {
    static update() {
        const actionsContainer = document.querySelector('.nav-actions');
        if (!actionsContainer) return;

        const user = AuthManager.getUser();
        if (user) {
            const adminBtn = user.role === 'admin'
                ? `<button class="btn btn-soft btn-sm" onclick="window.location.href='admin.html'">
                       <i class="fas fa-gauge-high"></i> Dashboard
                   </button>`
                : '';

            actionsContainer.innerHTML = `
                <div class="nav-user">
                    <span class="nav-user-name"><i class="fas fa-user-circle"></i> ${user.name}</span>
                </div>
                ${adminBtn}
                <button class="btn btn-ghost btn-sm" onclick="window.location.href='orders.html'">
                    <i class="fas fa-receipt"></i> Pesanan
                </button>
                <button class="btn btn-ghost btn-sm" id="logoutBtn">
                    <i class="fas fa-right-from-bracket"></i> Keluar
                </button>`;
            document.getElementById('logoutBtn')?.addEventListener('click', () => {
                AuthManager.logout();
                Toast.success('Berhasil logout!');
                setTimeout(() => window.location.reload(), 500);
            });
        } else {
            actionsContainer.innerHTML = `
                <button class="btn btn-ghost" onclick="window.location.href='login.html'">
                    <i class="fas fa-right-to-bracket"></i> Masuk
                </button>
                <button class="btn btn-primary" onclick="window.location.href='register.html'">
                    <i class="fas fa-user-plus"></i> Daftar
                </button>`;
        }
    }
}

// ── Concert Renderer (for index page) ───────────────────
class ConcertApp {
    constructor() {
        this.concerts = [];
        this.activeGenre = 'all';
        this.searchKeyword = '';
    }

    async init() {
        NavbarRenderer.update();
        this.bindEvents();
        await this.loadConcerts();
    }

    bindEvents() {
        const navbar = document.getElementById('navbar');
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        const searchForm = document.getElementById('searchForm');
        const searchInput = document.getElementById('searchInput');
        const genreFilter = document.getElementById('genreFilter');
        const filterTabs = document.getElementById('filterTabs');

        if (navbar) {
            window.addEventListener('scroll', () => navbar.classList.toggle('scrolled', window.scrollY > 30));
        }
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                const isOpen = navMenu.classList.toggle('open');
                navToggle.setAttribute('aria-expanded', isOpen);
                navToggle.innerHTML = `<i class="fas fa-${isOpen ? 'xmark' : 'bars'}"></i>`;
            });
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('open');
                    navToggle.setAttribute('aria-expanded', 'false');
                    navToggle.innerHTML = '<i class="fas fa-bars"></i>';
                });
            });
        }
        if (searchInput) {
            searchInput.addEventListener('input', () => { this.searchKeyword = searchInput.value; this.renderConcerts(); });
        }
        if (genreFilter) {
            genreFilter.addEventListener('change', (e) => this.setActiveGenre(e.target.value));
        }
        if (filterTabs) {
            filterTabs.addEventListener('click', (e) => {
                const tab = e.target.closest('[data-genre]');
                if (tab) this.setActiveGenre(tab.dataset.genre);
            });
        }
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                document.getElementById('concerts')?.scrollIntoView({ behavior: 'smooth' });
            });
        }
    }

    async loadConcerts() {
        const grid = document.getElementById('concertGrid');
        if (!grid) return;
        grid.innerHTML = '<div class="spinner"></div>';

        try {
            const data = await APIClient.get('/api/concerts');
            this.concerts = data.concerts || [];
            this.renderGenreControls();
            this.renderConcerts();
        } catch (err) {
            this.concerts = ConcertApp.FALLBACK_DATA;
            this.renderGenreControls();
            this.renderConcerts();
        }
    }

    setActiveGenre(genre) {
        this.activeGenre = genre;
        const genreFilter = document.getElementById('genreFilter');
        if (genreFilter) genreFilter.value = genre;
        this.renderGenreControls();
        this.renderConcerts();
    }

    getGenres() {
        return ['all', ...new Set(this.concerts.map(c => c.genre))];
    }

    renderGenreControls() {
        const genres = this.getGenres();
        const genreFilter = document.getElementById('genreFilter');
        const filterTabs = document.getElementById('filterTabs');

        if (genreFilter) {
            genreFilter.innerHTML = genres.map(g => `<option value="${g}">${g === 'all' ? 'Semua genre' : g}</option>`).join('');
            genreFilter.value = this.activeGenre;
        }
        if (filterTabs) {
            filterTabs.innerHTML = genres.map(g => `
                <button class="filter-tab ${g === this.activeGenre ? 'active' : ''}" type="button" data-genre="${g}">
                    ${g === 'all' ? 'Semua' : g}
                </button>`).join('');
        }
    }

    getFilteredConcerts() {
        const kw = this.searchKeyword.toLowerCase().trim();
        return this.concerts.filter(c => {
            const searchable = `${c.title} ${(c.artists || []).join(' ')} ${c.venue || ''} ${c.genre}`.toLowerCase();
            const matchKw = !kw || searchable.includes(kw);
            const matchGenre = this.activeGenre === 'all' || c.genre === this.activeGenre;
            return matchKw && matchGenre;
        });
    }

    renderConcerts() {
        const grid = document.getElementById('concertGrid');
        const emptyState = document.getElementById('emptyState');
        if (!grid) return;

        const filtered = this.getFilteredConcerts();
        const icons = ['fas fa-music', 'fas fa-guitar', 'fas fa-record-vinyl', 'fas fa-headphones', 'fas fa-microphone'];

        grid.innerHTML = filtered.map((c, i) => {
            const artists = c.artistLineup ? c.artistLineup.join(', ') : (c.artists || '');
            const venue = c.venueName || c.venue || '';
            const city = c.venueAddress || c.city || '';
            const dateStr = c.dateTime || c.date || '';
            const d = new Date(dateStr);
            const day = isNaN(d) ? '?' : d.getDate();
            const month = isNaN(d) ? '' : d.toLocaleString('id-ID', { month: 'short' });
            const price = c.minPrice ? `Rp${c.minPrice.toLocaleString('id-ID')}` : (c.price || 'Rp0');
            const slots = c.totalSlots ?? c.slots ?? 0;
            const concertId = c.concertId || '';
            const icon = icons[i % icons.length];

            return `
                <article class="concert-card">
                    <div class="card-top alt-${i % 3}">
                        <div class="concert-date"><strong>${day}</strong><small>${month}</small></div>
                        <i class="${icon}"></i>
                    </div>
                    <div class="card-body">
                        <div>
                            <span class="genre-pill">${c.genre}</span>
                            <h3 class="concert-title">${c.title}</h3>
                        </div>
                        <p class="card-meta"><i class="fas fa-users"></i><span>${artists}</span></p>
                        <p class="card-meta"><i class="fas fa-location-dot"></i><span>${venue}${city ? ', ' + city : ''}</span></p>
                        <div class="ticket-row">
                            <div>
                                <span class="price">Mulai dari <strong>${price}</strong></span>
                                <span class="availability">${slots} tiket tersedia</span>
                            </div>
                            <button class="btn btn-soft btn-sm" data-book-concert="${concertId}" data-book-title="${c.title}">
                                <i class="fas fa-ticket"></i> Beli
                            </button>
                        </div>
                    </div>
                </article>`;
        }).join('');

        if (emptyState) emptyState.classList.toggle('show', filtered.length === 0);

        grid.querySelectorAll('[data-book-concert]').forEach(btn => {
            btn.addEventListener('click', () => {
                const cid = btn.dataset.bookConcert;
                const title = btn.dataset.bookTitle;
                if (AuthManager.requireAuth()) {
                    window.location.href = `booking.html?concertId=${encodeURIComponent(cid)}&concert=${encodeURIComponent(title)}`;
                }
            });
        });
    }

    static FALLBACK_DATA = [
        { title: 'Java Jazz Festival 2026', artistLineup: ['Tulus', 'Ardhito Pramono', 'Nadin Amizah'], venueName: 'JIExpo Kemayoran', venueAddress: 'Jakarta', dateTime: '2026-08-15T19:00:00', genre: 'Jazz', minPrice: 850000, totalSlots: 124, concertId: '' },
        { title: 'Rockdut Fest', artistLineup: ['Denny Caknan', 'Mahalini', 'Fiersa Besari'], venueName: 'Stadion GBK', venueAddress: 'Jakarta', dateTime: '2026-09-20T19:00:00', genre: 'Pop', minPrice: 450000, totalSlots: 89, concertId: '' },
        { title: 'Indie Showcase Night', artistLineup: ['Hindia', 'Reality Club', 'Lomba Sihir'], venueName: 'Tennis Indoor Senayan', venueAddress: 'Jakarta', dateTime: '2026-10-05T19:00:00', genre: 'Indie', minPrice: 375000, totalSlots: 56, concertId: '' },
        { title: 'Electro Pulse Arena', artistLineup: ['Dipha Barus', 'Weird Genius', 'Bleu Clair'], venueName: 'Beach City International Stadium', venueAddress: 'Jakarta', dateTime: '2026-11-22T19:00:00', genre: 'EDM', minPrice: 620000, totalSlots: 73, concertId: '' }
    ];
}

// ── Orders Manager (New OOP Layer for orders page) ───────
class OrdersApp {
    async init() {
        NavbarRenderer.update();
        if (!AuthManager.requireAuth('index.html')) return;
        
        // Daftarkan fungsi ke window agar bisa dipanggil dari HTML string (onclick)
        window.payOrder = (orderId) => this.payOrder(orderId);
        window.cancelOrder = (orderId) => this.cancelOrder(orderId);
        window.showTicketInfo = () => this.showTicketInfo();

        await this.loadOrders();
    }

    async loadOrders() {
        const container = document.getElementById('ordersContainer');
        if (!container) return;
        container.innerHTML = '<div class="spinner"></div>';

        try {
            const user = AuthManager.getUser();
            const data = await APIClient.get('/api/orders/user/' + user.userId);
            const orders = data.orders || [];
            
            if (orders.length === 0) {
                container.innerHTML = '<div class="empty-state show">Belum ada pesanan tiket. <br><br><a href="index.html" class="btn btn-primary btn-sm">Cari Konser</a></div>';
                return;
            }
            
            orders.sort((a,b) => new Date(b.orderDate) - new Date(a.orderDate));
            
            container.innerHTML = orders.map(o => {
                const date = new Date(o.orderDate).toLocaleString('id-ID');
                let actionHtml = '';
                
                if (o.status === 'pending') {
                    actionHtml = `
                        <div class="order-actions">
                            <button class="btn btn-success btn-sm" onclick="payOrder('${o.orderId}')"><i class="fas fa-money-bill-wave"></i> Bayar</button>
                            <button class="btn btn-danger btn-sm" onclick="cancelOrder('${o.orderId}')"><i class="fas fa-times"></i> Batal</button>
                        </div>
                    `;
                } else if (o.status === 'paid') {
                    actionHtml = `
                        <div class="order-actions">
                            <button class="btn btn-soft btn-sm" onclick="showTicketInfo()"><i class="fas fa-qrcode"></i> Lihat Tiket</button>
                        </div>
                    `;
                }
                
                return `
                    <div class="order-card">
                        <div class="order-header">
                            <h3>${o.concertTitle}</h3>
                            <span class="order-status ${o.status}">${o.status === 'paid' ? 'LUNAS' : (o.status === 'pending' ? 'PENDING' : 'DIBATALKAN')}</span>
                        </div>
                        <div class="order-details">
                            <span>ID Pesanan</span><span>${o.orderId}</span>
                            <span>Tanggal Pesan</span><span>${date}</span>
                            <span>Total Bayar</span><span>Rp${o.totalAmount.toLocaleString('id-ID')}</span>
                        </div>
                        ${actionHtml}
                    </div>
                `;
            }).join('');
        } catch (err) {
            container.innerHTML = '<div class="empty-state show">Gagal memuat pesanan. Pastikan server backend API berjalan.</div>';
            Toast.error('Gagal memuat daftar pesanan.');
        }
    }

    async payOrder(orderId) {
        const { value: paymentMethod } = await Swal.fire({
            title: 'Pilih Metode Pembayaran',
            input: 'select',
            inputOptions: {
                'transfer': 'Transfer Bank',
                'gopay': 'GoPay / ShopeePay',
                'ovo': 'OVO',
                'qris': 'QRIS / M-Banking'
            },
            inputPlaceholder: '--- Pilih Metode ---',
            showCancelButton: true,
            confirmButtonColor: '#28a745',
            cancelButtonColor: '#dc3545',
            confirmButtonText: 'Lanjutkan Pembayaran',
            cancelButtonText: 'Batal',
            inputValidator: (value) => {
                if (!value) return 'Kamu harus memilih metode pembayaran terlebih dahulu!';
            }
        });

        if (paymentMethod) {
            try {
                await APIClient.post('/api/payments', { orderId: orderId, method: paymentMethod });
                Swal.fire({
                    title: 'Pembayaran Berhasil!',
                    text: `Metode ${paymentMethod.toUpperCase()} sukses diproses.`,
                    icon: 'success',
                    confirmButtonColor: '#28a745'
                });
                this.loadOrders();
            } catch (err) {
                Toast.error(err.message);
            }
        }
    }

    async cancelOrder(orderId) {
        const result = await Swal.fire({
            title: 'Apakah Anda yakin?',
            text: 'Pesanan yang dibatalkan tidak dapat dikembalikan.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Ya, Batalkan Pesanan',
            cancelButtonText: 'Kembali'
        });

        if (result.isConfirmed) {
            try {
                await APIClient.post('/api/orders/cancel', { orderId: orderId });
                Swal.fire({
                    title: 'Dibatalkan!',
                    text: 'Pesanan Anda telah berhasil dibatalkan.',
                    icon: 'success',
                    confirmButtonColor: '#28a745'
                });
                this.loadOrders();
            } catch (err) {
                Toast.error(err.message);
            }
        }
    }

    showTicketInfo() {
        Swal.fire({
            title: 'Informasi Pengiriman Tiket',
            text: 'Tiket QR Code akan dikirimkan ke email Anda mendekati hari H pelaksanaan konser.',
            icon: 'info',
            confirmButtonColor: '#28a745'
        });
    }
}

// ── Auto-init berdasarkan halaman ───────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page;

    if (page === 'home') {
        new ConcertApp().init();
    } else if (page === 'orders') {
        new OrdersApp().init(); // Otomatis inisialisasi class halaman orders
    } else {
        NavbarRenderer.update();
    }
});