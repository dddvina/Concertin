// State
let currentUser = null;
try {
    currentUser = JSON.parse(localStorage.getItem('concertin_user'));
} catch (e) {
    currentUser = null;
}

document.addEventListener('DOMContentLoaded', () => {
    updateNav();
    
    // Auto Back Button
    if (window.location.pathname !== '/' && !window.location.pathname.endsWith('index.html')) {
        if (!window.location.pathname.endsWith('login.html') && !window.location.pathname.endsWith('register.html')) {
            const backBtn = document.createElement('button');
            backBtn.className = 'btn btn-outline';
            backBtn.innerHTML = '<i class="fas fa-arrow-left"></i> Kembali';
            backBtn.style.cssText = 'position: fixed; bottom: 2rem; left: 2rem; z-index: 1000; background: rgba(31, 40, 51, 0.9); backdrop-filter: blur(10px); box-shadow: 0 5px 15px rgba(0,0,0,0.5);';
            backBtn.onclick = () => history.back();
            document.body.appendChild(backBtn);
        }
    }
    
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success) {
                    localStorage.setItem('concertin_user', JSON.stringify(data.data));
                    window.location.href = 'index.html';
                } else {
                    alert(`Login gagal: ${data.message}`);
                }
            } catch (err) {
                alert("Kesalahan jaringan.");
            }
        });
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                const data = await res.json();
                if (data.success) {
                    alert('Registrasi berhasil! Silakan login.');
                    window.location.href = 'login.html';
                } else {
                    alert(`Registrasi gagal: ${data.message}`);
                }
            } catch (err) {
                alert("Kesalahan jaringan.");
            }
        });
    }

    // Admin Register form
    const adminRegisterForm = document.getElementById('adminRegisterForm');
    if (adminRegisterForm) {
        adminRegisterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('adminRegName').value;
            const email = document.getElementById('adminRegEmail').value;
            const password = document.getElementById('adminRegPassword').value;
            const role = document.getElementById('adminRegRole').value;
            try {
                const res = await fetch('/api/admin/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password, role })
                });
                const data = await res.json();
                if (data.success) {
                    alert(`Registrasi akun ${role} berhasil!`);
                    adminRegisterForm.reset();
                } else {
                    alert(`Registrasi gagal: ${data.message}`);
                }
            } catch (err) {
                alert("Kesalahan jaringan.");
            }
        });
    }

    // Index page load
    const concertGrid = document.getElementById('concertGrid');
    if (concertGrid) {
        loadConcertsHome();
    }
});

function updateNav() {
    const navActions = document.getElementById('navActions');
    if (!navActions) return;
    
    if (currentUser) {
        let adminLink = '';
        if (currentUser.role === 'admin') {
            adminLink = `<a href="admin.html" style="color: var(--accent); margin-right: 15px; font-weight: 600; text-decoration: none;"><i class="fas fa-user-shield"></i> Admin Panel</a>`;
        }
        navActions.innerHTML = `
            ${adminLink}
            <a href="tickets.html" style="color: var(--accent); margin-right: 15px; font-weight: 600; text-decoration: none;"><i class="fas fa-ticket-alt"></i> Tiket Saya</a>
            <span style="color: white; margin-right: 15px; font-weight: 600;">Hi, ${currentUser.name}</span>
            <button class="btn btn-outline" onclick="logout()">Keluar</button>
        `;
    } else {
        navActions.innerHTML = `
            <a href="login.html" class="btn btn-outline" style="margin-right: 10px;">Masuk</a>
            <a href="register.html" class="btn btn-primary">Daftar</a>
        `;
    }
}

function logout() {
    localStorage.removeItem('concertin_user');
    window.location.href = 'index.html';
}

async function loadConcertsHome() {
    const grid = document.getElementById('concertGrid');
    grid.innerHTML = '<p style="color:white; text-align:center; width:100%;">Memuat data...</p>';
    try {
        const res = await fetch('/api/concerts');
        const data = await res.json();
        if (data.success && data.data.length > 0) {
            grid.innerHTML = '';
            data.data.forEach(c => {
                const dateObj = new Date(c.dateTime);
                const dateStr = dateObj.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
                grid.innerHTML += `
                    <div class="concert-card" onclick="window.location.href='detail.html?id=${c.concertId}'">
                        <div class="date-badge">${dateStr}</div>
                        <span class="concert-genre">${c.genre}</span>
                        <h3 class="concert-title">${c.title}</h3>
                        <div class="concert-artists"><i class="fas fa-users"></i> ${c.artistLineup.join(', ')}</div>
                        <div class="concert-venue"><i class="fas fa-map-marker-alt"></i> ${c.venueName}</div>
                        <div class="card-footer">
                            <span class="status ${c.status}">${c.status.toUpperCase()}</span>
                            <span class="btn btn-outline" style="padding: 0.5rem 1rem; font-size: 0.9rem;">Lihat Detail</span>
                        </div>
                    </div>
                `;
            });
        } else {
            grid.innerHTML = '<p style="color:white;">Belum ada jadwal konser.</p>';
        }
    } catch (e) {
        grid.innerHTML = '<p style="color:red; text-align:center; width:100%;">Gagal memuat konser. Pastikan server aktif.</p>';
    }
}

// Detail page functions
let currentConcert = null;
async function loadConcertDetail() {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    if (!id) return window.location.href = 'index.html';

    const hero = document.getElementById('detailHero');
    const ticketList = document.getElementById('ticketList');
    
    try {
        const res = await fetch('/api/concerts');
        const data = await res.json();
        currentConcert = data.data.find(c => c.concertId === id);
        
        if (!currentConcert) throw new Error("Konser tidak ditemukan");

        const dateObj = new Date(currentConcert.dateTime);
        const dateStr = dateObj.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

        hero.innerHTML = `
            <div class="detail-info">
                <span class="status ${currentConcert.status}" style="margin-bottom: 1rem;">${currentConcert.status.toUpperCase()}</span>
                <h1>${currentConcert.title}</h1>
                <p style="font-size: 1.2rem; margin-bottom: 1rem;"><i class="fas fa-calendar-alt"></i> ${dateStr}</p>
                <p style="font-size: 1.2rem; margin-bottom: 1rem;"><i class="fas fa-map-marker-alt"></i> ${currentConcert.venueName}</p>
                <p style="color: var(--text-secondary); margin-bottom: 2rem;">Rasakan pengalaman konser yang luar biasa bersama line up favoritmu.</p>
                <h3><i class="fas fa-users"></i> Lineup:</h3>
                <p style="font-size: 1.1rem; color: var(--accent); margin-top: 0.5rem;">${currentConcert.artistLineup.join(' • ')}</p>
            </div>
        `;

        const tRes = await fetch(`/api/tickets?concertId=${id}`);
        const tData = await tRes.json();
        
        if (tData.success && tData.data.length > 0) {
            ticketList.innerHTML = '';
            tData.data.forEach(t => {
                const formatter = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });
                const isSoldOut = t.remainingQuota <= 0;
                ticketList.innerHTML += `
                    <div class="ticket-card" style="background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 15px; padding: 2rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; opacity: ${isSoldOut ? '0.5' : '1'}">
                        <div>
                            <h3 style="color: var(--accent); font-size: 1.5rem; margin-bottom: 0.5rem;">${t.category}</h3>
                            <p style="font-size: 1.2rem; font-weight: bold;">${formatter.format(t.price)}</p>
                            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">Sisa Kuota: ${t.remainingQuota}</p>
                        </div>
                        <div style="display: flex; gap: 1rem; align-items: center;">
                            <button class="btn btn-outline" onclick="showSeatPlan('${currentConcert.concertId}', '${t.ticketId}', '${t.category}', ${t.price}, ${t.remainingQuota})" ${isSoldOut ? 'disabled' : ''}>${isSoldOut ? 'Habis' : 'Pilih Kursi'}</button>
                        </div>
                    </div>
                `;
            });
        } else {
            ticketList.innerHTML = '<p>Tiket belum tersedia.</p>';
        }

    } catch (e) {
        hero.innerHTML = `<p>Gagal memuat detail konser.</p>`;
    }
}

function showSeatPlan(concertId, ticketId, category, price, maxQuota) {
    if (!currentUser) return alert("Harap masuk (login) terlebih dahulu."), window.location.href = 'login.html';
    let seats = '<div style="display:grid; grid-template-columns: repeat(10, 1fr); gap: 10px; margin-top:2rem;">';
    for(let i=1; i<=50; i++) {
        const isAvail = i <= maxQuota;
        seats += `<div onclick="${isAvail ? 'toggleSeat(this)' : ''}" class="seat" style="height:35px; background: ${isAvail ? 'var(--glass-bg)' : '#555'}; border: 1px solid ${isAvail ? 'var(--accent)' : '#444'}; border-radius:5px; cursor: ${isAvail ? 'pointer' : 'not-allowed'}; display:flex; align-items:center; justify-content:center; font-size:0.8rem;">${i}</div>`;
    }
    document.getElementById('ticketsSection').innerHTML = `
        <h2 class="section-title">Pilih Kursi - ${category}</h2>
        ${seats}</div>
        <div style="margin-top: 2rem; display: flex; justify-content: space-between; align-items: center;">
            <p style="font-size: 1.2rem;">Kursi terpilih: <span id="selCount" style="color:var(--accent); font-weight:bold;">0</span></p>
            <button class="btn btn-primary" onclick="proceedPlan('${concertId}', '${ticketId}', '${category}', ${price}, ${maxQuota})">Lanjut Pembayaran</button>
        </div>`;
}

function toggleSeat(el) {
    el.classList.toggle('selected');
    if (el.classList.contains('selected')) {
        el.style.background = 'var(--accent)';
        el.style.color = 'var(--bg-main)';
    } else {
        el.style.background = 'var(--glass-bg)';
        el.style.color = 'var(--text-primary)';
    }
    document.getElementById('selCount').innerText = document.querySelectorAll('.seat.selected').length;
}

function proceedPlan(concertId, ticketId, category, price, maxQuota) {
    const qty = document.querySelectorAll('.seat.selected').length;
    if (qty === 0 || qty > maxQuota) return alert("Pilih minimal 1 kursi dan maksimal sesuai kuota.");
    sessionStorage.setItem('pendingOrder', JSON.stringify({ concertId, ticketId, category, price, quantity: qty, concertTitle: currentConcert.title }));
    window.location.href = 'checkout.html';
}

// Checkout functions
async function loadCheckoutSummary() {
    if (!currentUser) return window.location.href = 'login.html';
    
    const orderData = JSON.parse(sessionStorage.getItem('pendingOrder'));
    if (!orderData) return window.location.href = 'index.html';

    const formatter = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });
    const total = orderData.price * orderData.quantity;

    document.getElementById('summaryCard').innerHTML = `
        <h3>Ringkasan Pesanan</h3>
        <div style="margin-top: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem;">
            <p style="font-weight: bold; font-size: 1.2rem; color: var(--accent);">${orderData.concertTitle}</p>
            <p style="margin-top: 0.5rem;">Kategori: ${orderData.category}</p>
            <p>Jumlah: ${orderData.quantity} tiket</p>
        </div>
        <div style="margin-top: 1rem; display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: bold;">
            <span>Total Tagihan</span>
            <span style="color: var(--accent);">${formatter.format(total)}</span>
        </div>
    `;
}

async function processPayment() {
    const orderData = JSON.parse(sessionStorage.getItem('pendingOrder'));
    if (!orderData) return;

    const btn = document.querySelector('.payment-card .btn-primary');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses GoPay...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userId: currentUser.userId,
                concertId: orderData.concertId,
                ticketId: orderData.ticketId,
                quantity: orderData.quantity
            })
        });

        const data = await res.json();
        
        setTimeout(() => {
            if (data.success) {
                let myTickets = JSON.parse(localStorage.getItem('myTickets') || '[]');
                
                for (let i = 0; i < orderData.quantity; i++) {
                    myTickets.push({
                        ticketId: `TKT-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
                        concertTitle: orderData.concertTitle,
                        category: orderData.category,
                        orderId: data.data.orderId,
                        userId: currentUser.userId,
                        purchasedAt: new Date().toISOString()
                    });
                }
                localStorage.setItem('myTickets', JSON.stringify(myTickets));
                
                alert("Pembayaran GoPay Berhasil!");
                sessionStorage.removeItem('pendingOrder');
                window.location.href = 'tickets.html';
            } else {
                alert(`Gagal membuat pesanan: ${data.message}`);
                btn.innerHTML = 'Bayar Sekarang';
                btn.disabled = false;
            }
        }, 2000);

    } catch (e) {
        alert("Terjadi kesalahan jaringan.");
        btn.innerHTML = 'Bayar Sekarang';
        btn.disabled = false;
    }
}

// Tiket Saya functions
function loadMyTickets() {
    if (!currentUser) return window.location.href = 'login.html';

    const container = document.getElementById('myTicketsContainer');
    const allTickets = JSON.parse(localStorage.getItem('myTickets') || '[]');
    const myTickets = allTickets.filter(t => t.userId === currentUser.userId);

    if (myTickets.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">Anda belum memiliki tiket.</p>';
        return;
    }

    container.innerHTML = '';
    myTickets.reverse().forEach(t => {
        const qrData = `VALIDATE:${t.ticketId}:${t.orderId}`;
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrData)}`;

        container.innerHTML += `
            <div class="qr-ticket" style="background: linear-gradient(135deg, #ffffff, #f0f0f0); color: #0b0c10; border-radius: 20px; padding: 2rem; text-align: center; width: 300px; box-shadow: 0 10px 30px rgba(102, 252, 241, 0.2);">
                <h3 style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.5rem; color: var(--bg-main);">${t.concertTitle}</h3>
                <p style="font-weight: 600; color: var(--accent-dark); margin-bottom: 1.5rem;">Kategori: ${t.category}</p>
                <div style="background: white; padding: 10px; display: inline-block; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                    <img src="${qrUrl}" alt="QR Code" style="width: 150px; height: 150px;">
                </div>
                <p style="font-family: monospace; font-size: 0.9rem; margin-bottom: 1rem; font-weight: 600; color: #555;">ID: ${t.ticketId}</p>
                <button class="btn btn-primary" style="width: 100%; padding: 0.8rem; border-radius: 10px;" onclick="validateTicket('${t.ticketId}')">Simulasikan Validasi</button>
            </div>
        `;
    });
}

function validateTicket(ticketId) {
    alert(`Memindai tiket ${ticketId}...\n\n✅ TIKET VALID!\nSilakan masuk ke venue tanpa antrian.`);
}
