/**
 * ConcertIn Admin Dashboard (OOP Architecture)
 * Mengelola panel admin: tambah konser, tambah tiket, hapus konser.
 * Bergantung pada class dari script.js (AuthManager, APIClient, Toast, NavbarRenderer).
 */

// ── Admin App (Main Controller) ─────────────────────────
class AdminApp {
    constructor() {
        this.concerts = [];
        this._pendingDeleteId = null;
    }

    async init() {
        // Pastikan user sudah login dan admin
        const user = AuthManager.getUser();
        if (!user || user.role !== 'admin') {
            Toast.error('Akses ditolak. Hanya admin yang bisa mengakses halaman ini.');
            setTimeout(() => window.location.href = 'index.html', 1200);
            return;
        }

        this._renderTopbarUser(user);
        this._bindSidebar();
        this._bindPanelNav();
        this._bindForms();
        this._bindDeleteModal();
        this._bindLogout();

        await this._loadAll();
    }

    // ── Topbar ──────────────────────────────────────────
    _renderTopbarUser(user) {
        const el = document.getElementById('topbarUser');
        if (el) {
            el.innerHTML = `<span class="nav-user-name"><i class="fas fa-user-shield"></i> ${user.name}</span>`;
        }
    }

    // ── Sidebar Toggle (mobile) ─────────────────────────
    _bindSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebarToggle');

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.id = 'sidebarOverlay';
        document.body.appendChild(overlay);

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
                overlay.classList.toggle('active');
            });
        }
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // ── Panel Navigation ────────────────────────────────
    _bindPanelNav() {
        const links = document.querySelectorAll('.sidebar-link[data-panel]');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');

        links.forEach(link => {
            link.addEventListener('click', () => {
                const target = link.dataset.panel;

                // Update active sidebar
                links.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Show target panel
                document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
                const panelMap = {
                    'overview': 'panelOverview',
                    'add-concert': 'panelAddConcert',
                    'add-ticket': 'panelAddTicket',
                    'delete-concert': 'panelDeleteConcert'
                };
                const panel = document.getElementById(panelMap[target]);
                if (panel) {
                    panel.classList.remove('active');
                    // Force reflow for re-triggering animation
                    void panel.offsetWidth;
                    panel.classList.add('active');
                }

                // Close mobile sidebar
                if (sidebar) sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('active');

                // Reload data for specific panels
                if (target === 'add-ticket') this._loadConcertSelect();
                if (target === 'delete-concert') this._renderDeleteTable();
                if (target === 'overview') this._loadAll();
            });
        });
    }

    // ── Forms ───────────────────────────────────────────
    _bindForms() {
        const concertForm = document.getElementById('addConcertForm');
        const ticketForm = document.getElementById('addTicketForm');

        if (concertForm) {
            concertForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this._submitConcert();
            });
        }

        if (ticketForm) {
            ticketForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this._submitTicket();
            });
        }
    }

    // ── Delete Modal ────────────────────────────────────
    _bindDeleteModal() {
        const modal = document.getElementById('deleteModal');
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        const cancelBtn = document.getElementById('cancelDeleteBtn');

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this._pendingDeleteId = null;
                modal.classList.remove('active');
            });
        }
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this._pendingDeleteId = null;
                    modal.classList.remove('active');
                }
            });
        }
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this._executeDelete());
        }
    }

    // ── Logout ──────────────────────────────────────────
    _bindLogout() {
        const btn = document.getElementById('adminLogoutBtn');
        if (btn) {
            btn.addEventListener('click', () => {
                AuthManager.logout();
                Toast.success('Berhasil logout!');
                setTimeout(() => window.location.href = 'index.html', 600);
            });
        }
    }

    // ── Load All Data ───────────────────────────────────
    async _loadAll() {
        await Promise.all([
            this._loadConcerts(),
            this._loadStatistics()
        ]);
    }

    // ── Load Concerts ───────────────────────────────────
    async _loadConcerts() {
        try {
            const data = await APIClient.get('/api/concerts');
            this.concerts = data.concerts || [];
            this._renderOverviewTable();
            this._renderDeleteTable();
        } catch (err) {
            this.concerts = [];
            this._renderOverviewTable();
            this._renderDeleteTable();
        }
    }

    // ── Load Statistics ─────────────────────────────────
    async _loadStatistics() {
        try {
            const data = await APIClient.get('/api/statistics');
            const s = data.statistics || {};

            const el = (id) => document.getElementById(id);
            const totalConcerts = this.concerts.length;
            el('statConcerts').textContent = totalConcerts;
            el('statUsers').textContent = s.total_users ?? '—';
            el('statTicketsSold').textContent = s.tickets_sold ?? '—';

            const revenue = s.total_revenue ?? 0;
            el('statRevenue').textContent = `Rp${revenue.toLocaleString('id-ID')}`;
        } catch (err) {
            // Silently fail, stats just stay as "—"
        }
    }

    // ── Render Overview Table ───────────────────────────
    _renderOverviewTable() {
        const tbody = document.getElementById('overviewConcertBody');
        if (!tbody) return;

        if (this.concerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="table-empty">Belum ada konser terdaftar.</td></tr>';
            return;
        }

        tbody.innerHTML = this.concerts.map((c, i) => {
            const artists = c.artistLineup ? c.artistLineup.join(', ') : '';
            const venue = `${c.venueName || ''}, ${c.venueAddress || ''}`;
            const d = new Date(c.dateTime);
            const dateStr = isNaN(d) ? '-' : d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
            const status = c.status || 'upcoming';

            return `
                <tr>
                    <td>${i + 1}</td>
                    <td><strong>${c.title}</strong></td>
                    <td>${artists}</td>
                    <td>${venue}</td>
                    <td>${dateStr}</td>
                    <td><span class="table-status ${status}">${status}</span></td>
                </tr>`;
        }).join('');
    }

    // ── Render Delete Table ─────────────────────────────
    _renderDeleteTable() {
        const tbody = document.getElementById('deleteConcertBody');
        if (!tbody) return;

        if (this.concerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="table-empty">Belum ada konser untuk dihapus.</td></tr>';
            return;
        }

        tbody.innerHTML = this.concerts.map((c, i) => {
            const d = new Date(c.dateTime);
            const dateStr = isNaN(d) ? '-' : d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });

            return `
                <tr>
                    <td>${i + 1}</td>
                    <td><strong>${c.title}</strong></td>
                    <td>${c.genre}</td>
                    <td>${c.venueName || ''}</td>
                    <td>${dateStr}</td>
                    <td>
                        <button class="btn-delete-row" data-delete-id="${c.concertId}" data-delete-title="${c.title}">
                            <i class="fas fa-trash"></i> Hapus
                        </button>
                    </td>
                </tr>`;
        }).join('');

        // Bind delete buttons
        tbody.querySelectorAll('[data-delete-id]').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.deleteId;
                const title = btn.dataset.deleteTitle;
                this._showDeleteModal(id, title);
            });
        });
    }

    // ── Load Concert Select (for Add Ticket) ────────────
    async _loadConcertSelect() {
        const select = document.getElementById('ticketConcertSelect');
        if (!select) return;

        try {
            if (this.concerts.length === 0) {
                const data = await APIClient.get('/api/concerts');
                this.concerts = data.concerts || [];
            }

            if (this.concerts.length === 0) {
                select.innerHTML = '<option value="">Tidak ada konser tersedia</option>';
                return;
            }

            select.innerHTML = '<option value="">Pilih konser...</option>' +
                this.concerts.map(c =>
                    `<option value="${c.concertId}">${c.title}</option>`
                ).join('');
        } catch {
            select.innerHTML = '<option value="">Gagal memuat konser</option>';
        }
    }

    // ── Submit: Tambah Konser ────────────────────────────
    async _submitConcert() {
        const user = AuthManager.getUser();
        const btn = document.getElementById('submitConcertBtn');

        const title = document.getElementById('concertTitle').value.trim();
        const artistsRaw = document.getElementById('concertArtists').value.trim();
        const venue = document.getElementById('concertVenue').value.trim();
        const address = document.getElementById('concertAddress').value.trim();
        const dateTime = document.getElementById('concertDate').value;
        const genre = document.getElementById('concertGenre').value;

        if (!title || !artistsRaw || !venue || !address || !dateTime || !genre) {
            Toast.error('Semua field wajib diisi!');
            return;
        }

        const artistLineup = artistsRaw.split(',').map(a => a.trim()).filter(a => a);

        btn.classList.add('loading');
        btn.innerHTML = '<i class="fas fa-spinner"></i> Menyimpan...';

        try {
            await APIClient.post('/api/concerts', {
                requesterId: user.userId,
                title,
                artistLineup,
                venueName: venue,
                venueAddress: address,
                dateTime,
                genre,
                status: 'upcoming'
            });

            Toast.success('🎉 Konser berhasil ditambahkan!');
            document.getElementById('addConcertForm').reset();

            // Reload data
            await this._loadConcerts();
        } catch (err) {
            Toast.error(err.message || 'Gagal menambahkan konser.');
        } finally {
            btn.classList.remove('loading');
            btn.innerHTML = '<i class="fas fa-paper-plane"></i> Simpan Konser';
        }
    }

    // ── Submit: Tambah Tiket ────────────────────────────
    async _submitTicket() {
        const user = AuthManager.getUser();
        const btn = document.getElementById('submitTicketBtn');

        const concertId = document.getElementById('ticketConcertSelect').value;
        const category = document.getElementById('ticketCategory').value;
        const price = parseFloat(document.getElementById('ticketPrice').value);
        const totalQuota = parseInt(document.getElementById('ticketQuota').value);

        if (!concertId || !category || isNaN(price) || isNaN(totalQuota)) {
            Toast.error('Semua field wajib diisi dengan benar!');
            return;
        }

        btn.classList.add('loading');
        btn.innerHTML = '<i class="fas fa-spinner"></i> Menyimpan...';

        try {
            await APIClient.post('/api/tickets', {
                requesterId: user.userId,
                concertId,
                category,
                price,
                totalQuota,
                remainingQuota: totalQuota
            });

            Toast.success(`🎫 Tiket ${category} berhasil ditambahkan!`);
            document.getElementById('addTicketForm').reset();
        } catch (err) {
            Toast.error(err.message || 'Gagal menambahkan tiket.');
        } finally {
            btn.classList.remove('loading');
            btn.innerHTML = '<i class="fas fa-paper-plane"></i> Simpan Tiket';
        }
    }

    // ── Delete: Show Modal ──────────────────────────────
    _showDeleteModal(concertId, title) {
        this._pendingDeleteId = concertId;
        const modal = document.getElementById('deleteModal');
        const text = document.getElementById('deleteModalText');
        if (text) {
            text.innerHTML = `Konser <strong>"${title}"</strong> beserta semua tiketnya akan dihapus permanen. Lanjutkan?`;
        }
        modal.classList.add('active');
    }

    // ── Delete: Execute ─────────────────────────────────
    async _executeDelete() {
        if (!this._pendingDeleteId) return;

        const user = AuthManager.getUser();
        const modal = document.getElementById('deleteModal');
        const btn = document.getElementById('confirmDeleteBtn');

        btn.classList.add('loading');
        btn.innerHTML = '<i class="fas fa-spinner"></i> Menghapus...';

        try {
            const url = `/api/concerts/${this._pendingDeleteId}?requesterId=${encodeURIComponent(user.userId)}`;
            await APIClient.request(url, { method: 'DELETE' });

            Toast.success('🗑️ Konser berhasil dihapus!');
            modal.classList.remove('active');
            this._pendingDeleteId = null;

            // Reload data
            await this._loadConcerts();
            await this._loadStatistics();
        } catch (err) {
            Toast.error(err.message || 'Gagal menghapus konser.');
        } finally {
            btn.classList.remove('loading');
            btn.innerHTML = '<i class="fas fa-trash"></i> Hapus';
        }
    }
}

// ── Init on DOM ready ───────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.dataset.page === 'admin') {
        new AdminApp().init();
    }
});
