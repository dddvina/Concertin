"""
Main CLI Application untuk ConcertIn.
Menyediakan antarmuka interaktif untuk pengguna sesuai skenario penggunaan.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService
from services.concert_service import ConcertService
from services.ticket_service import TicketService
from services.order_service import OrderService
from services.payment_service import PaymentService
from models.order_item import OrderItem
from repositories.json_repository import JsonRepository
from utils.exceptions import ConcertInException


def clear_screen():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Mencetak header dengan format yang konsisten."""
    print("\n" + "=" * 60)
    print(f" {title:^58}")
    print("=" * 60)


def print_separator():
    """Mencetak garis pemisah."""
    print("-" * 60)


def pause():
    """Menjeda aplikasi hingga pengguna menekan Enter."""
    input("\nTekan Enter untuk melanjutkan...")


# ── MENU UTAMA ──────────────────────────────────────────

def menu_utama():
    """Menu utama aplikasi."""
    while True:
        clear_screen()
        print_header("SELAMAT DATANG DI CONCERTIN")
        print("1. Login")
        print("2. Register")
        print("0. Keluar")
        print_separator()

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            user = menu_login()
            if user:
                if user.role == "admin":
                    menu_admin(user)
                else:
                    menu_customer(user)
        elif pilihan == "2":
            menu_register()
        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan ConcertIn! 🎵")
            sys.exit(0)
        else:
            print("\n[!] Pilihan tidak valid.")
            pause()


def menu_login():
    """Menu login pengguna."""
    print_header("LOGIN")
    try:
        email = input("Email    : ").strip()
        password = input("Password : ").strip()

        user = UserService.login(email, password)
        print(f"\n[✓] Login berhasil! Selamat datang, {user.name}.")
        pause()
        return user
    except ConcertInException as e:
        print(f"\n[✗] {e}")
        pause()
        return None


def menu_register():
    """Menu registrasi pengguna (otomatis sebagai customer)."""
    print_header("REGISTER")
    try:
        name = input("Nama lengkap  : ").strip()
        email = input("Email         : ").strip()
        password = input("Password      : ").strip()
        role = "cust"

        UserService.register(name, email, password, role)
        print("\n[✓] Registrasi berhasil! Silakan login.")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


# ── MENU CUSTOMER ───────────────────────────────────────

def menu_customer(user):
    """Menu untuk role customer."""
    menu_options = {
        "1": lihat_semua_konser,
        "2": cari_konser,
        "3": detail_konser,
        "4": lambda: pesan_tiket(user),
        "5": lambda: bayar_pesanan(user),
        "6": lambda: tiket_saya(user),
        "7": lambda: riwayat_pesanan(user),
        "8": lambda: batalkan_pesanan(user),
    }

    while True:
        clear_screen()
        print_header("MENU CUSTOMER")
        print(f"Halo, {user.name}!\n")
        print("1. Lihat Semua Konser")
        print("2. Cari Konser")
        print("3. Detail Konser")
        print("4. Pesan Tiket")
        print("5. Bayar Pesanan")
        print("6. Tiket Saya")
        print("7. Riwayat Pesanan")
        print("8. Batalkan Pesanan")
        print("0. Logout")
        print_separator()

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "0":
            user.logout()
            print("\n[✓] Logout berhasil.")
            pause()
            return

        action = menu_options.get(pilihan)
        if action:
            action()
        else:
            print("\n[!] Pilihan tidak valid.")
            pause()


# ── MENU ADMIN ──────────────────────────────────────────

def menu_admin(user):
    """Menu untuk role admin."""
    menu_options = {
        "1": lihat_semua_konser,
        "2": cari_konser,
        "3": detail_konser,
        "4": lambda: pesan_tiket(user),
        "5": lambda: bayar_pesanan(user),
        "6": lambda: tiket_saya(user),
        "7": lambda: riwayat_pesanan(user),
        "8": lambda: batalkan_pesanan(user),
        "9": tambah_konser,
        "10": tambah_tiket,
        "11": lihat_semua_order,
        "12": validasi_tiket,
        "13": lihat_statistik,
    }

    while True:
        clear_screen()
        print_header("MENU ADMIN")
        print(f"Halo, {user.name}!\n")
        print("1. Lihat Semua Konser")
        print("2. Cari Konser")
        print("3. Detail Konser")
        print("4. Pesan Tiket")
        print("5. Bayar Pesanan")
        print("6. Tiket Saya")
        print("7. Riwayat Pesanan")
        print("8. Batalkan Pesanan")
        print("9. Tambah Konser Baru")
        print("10. Tambah Tiket untuk Konser")
        print("11. Lihat Semua Order")
        print("12. Validasi Tiket di Venue")
        print("13. Statistik")
        print("0. Logout")
        print_separator()

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "0":
            user.logout()
            print("\n[✓] Logout berhasil.")
            pause()
            return

        action = menu_options.get(pilihan)
        if action:
            action()
        else:
            print("\n[!] Pilihan tidak valid.")
            pause()


# ── IMPLEMENTASI FITUR CUSTOMER ─────────────────────────

def lihat_semua_konser():
    """Menampilkan semua konser yang ada."""
    print_header("DAFTAR SEMUA KONSER")
    try:
        concerts = ConcertService.get_all_concerts()
        if not concerts:
            print("Belum ada konser terdaftar.")
        else:
            for i, c in enumerate(concerts, 1):
                print(f"[{i}] {c.title}")
                print(f"    Artis   : {', '.join(c.artistLineup)}")
                print(f"    Venue   : {c.venueName}, {c.venueAddress}")
                print(f"    Tanggal : {c.dateTime.strftime('%d %b %Y, %H:%M')}")
                print(f"    Genre   : {c.genre}")
                print(f"    Status  : {c.status}")
                print()
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def cari_konser():
    """Mencari konser berdasarkan keyword."""
    print_header("CARI KONSER")
    try:
        keyword = input("Masukkan keyword (judul/artis/venue/genre): ").strip()
        results = ConcertService.search_concerts(keyword)
        if not results:
            print(f"\nTidak ditemukan konser dengan keyword '{keyword}'.")
        else:
            print(f"\nDitemukan {len(results)} konser:\n")
            for i, c in enumerate(results, 1):
                print(f"[{i}] {c.title} | {', '.join(c.artistLineup)} | {c.genre}")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def _pilih_konser():
    """Helper untuk memilih konser dari daftar."""
    concerts = ConcertService.get_all_concerts()
    if not concerts:
        print("\nBelum ada konser terdaftar.")
        return None

    for i, c in enumerate(concerts, 1):
        print(f"[{i}] {c.title}")

    try:
        idx = int(input("\nPilih nomor konser: ")) - 1
        if 0 <= idx < len(concerts):
            return concerts[idx]
        print("\n[!] Pilihan di luar jangkauan.")
    except ValueError:
        print("\n[!] Input harus berupa angka.")
    return None


def detail_konser():
    """Menampilkan detail dan tiket konser."""
    print_header("DETAIL KONSER")
    try:
        c = _pilih_konser()
        if not c:
            pause()
            return

        print_separator()
        print(f"JUDUL   : {c.title}")
        print(f"ARTIS   : {', '.join(c.artistLineup)}")
        print(f"VENUE   : {c.venueName}, {c.venueAddress}")
        print(f"TANGGAL : {c.dateTime.strftime('%d %B %Y, %H:%M')}")
        print(f"GENRE   : {c.genre}")
        print(f"STATUS  : {c.status}")
        print("\nTIKET TERSEDIA:")

        tickets = TicketService.get_tickets_by_concert(c.concertId)
        if not tickets:
            print("Belum ada tiket.")
        else:
            for t in tickets:
                print(f"- {t.category:4} : Rp{t.price:,.0f} (Sisa: {t.remainingQuota})")
    except ConcertInException as e:
         print(f"\n[✗] {e}")
    pause()


def pesan_tiket(user):
    """Proses pemesanan tiket oleh user."""
    print_header("PESAN TIKET")
    try:
        c = _pilih_konser()
        if not c:
            pause()
            return

        tickets = TicketService.get_tickets_by_concert(c.concertId)
        if not tickets:
            print("\nBelum ada tiket untuk konser ini.")
            pause()
            return

        print("\nKategori Tiket:")
        for i, t in enumerate(tickets, 1):
            print(f"[{i}] {t.category} (Rp{t.price:,.0f}) - Sisa: {t.remainingQuota}")

        try:
            t_idx = int(input("Pilih kategori: ")) - 1
            if not (0 <= t_idx < len(tickets)):
                print("\n[!] Pilihan di luar jangkauan.")
                pause()
                return
            t = tickets[t_idx]
            qty = int(input("Jumlah tiket  : "))
            if qty <= 0:
                print("\n[!] Jumlah tiket harus positif.")
                pause()
                return
        except ValueError:
            print("\n[!] Input tidak valid.")
            pause()
            return

        # Ringkasan Pesanan
        subtotal = t.price * qty
        print_separator()
        print("RINGKASAN PESANAN")
        print(f"Konser   : {c.title}")
        print(f"Kategori : {t.category}")
        print(f"Jumlah   : {qty}")
        print(f"Subtotal : Rp{subtotal:,.0f}")
        print(f"TOTAL    : Rp{subtotal:,.0f}")
        print_separator()

        konfirmasi = input("Konfirmasi pesanan? (y/n): ").strip().lower()
        if konfirmasi == 'y':
            order = OrderService.create_order(user.userId, c.concertId, t.ticketId, qty)
            print(f"\n[✓] Pesanan berhasil dibuat!")
            print(f"    Order ID: {order.orderId}")
            print(f"    Status  : {order.status}")
        else:
            print("\n[i] Pemesanan dibatalkan.")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def _pilih_pesanan(user, status_filter=None):
    """Helper untuk memilih pesanan dari daftar user."""
    orders = OrderService.get_orders_by_user(user.userId)
    if status_filter:
        orders = [o for o in orders if o.status == status_filter]

    if not orders:
        status_msg = status_filter if status_filter else "semua"
        print(f"Tidak ada pesanan ({status_msg}).")
        return None

    for i, o in enumerate(orders, 1):
        print(f"[{i}] Order ID: {o.orderId} | Total: Rp{o.totalAmount:,.0f} | Status: {o.status.upper()}")

    try:
        idx = int(input("\nPilih pesanan: ")) - 1
        if 0 <= idx < len(orders):
            return orders[idx]
        print("\n[!] Pilihan di luar jangkauan.")
    except ValueError:
        print("\n[!] Input harus berupa angka.")
    return None


def bayar_pesanan(user):
    """Proses pembayaran pesanan pending."""
    print_header("BAYAR PESANAN")
    try:
        o = _pilih_pesanan(user, "pending")
        if not o:
            pause()
            return

        print("\nMetode Pembayaran:")
        print("1. Transfer Bank\n2. E-Wallet\n3. QRIS")
        metode_map = {"1": "transfer", "2": "ewallet", "3": "qris"}
        metode = metode_map.get(input("Pilih metode: ").strip())

        if not metode:
            print("\n[!] Metode tidak valid.")
            pause()
            return

        payment = PaymentService.process_payment(o.orderId, metode)
        print(f"\n[✓] Pembayaran BERHASIL!")
        print(f"    Payment ID : {payment.paymentId}")

        # Tampilkan Tiket Digital
        print_separator()
        print("🎫 TIKET DIGITAL ANDA 🎫")
        concert = ConcertService.get_concert_by_id(o.concertId)
        items = OrderItem.get_by_order(o.orderId)
        for item in items:
            ticket = TicketService.get_ticket_by_id(item.ticketId)
            print(f"Kode Tiket : {item.itemId}")
            print(f"Konser     : {concert.title}")
            print(f"Kategori   : {ticket.category}")
            print(f"Tanggal    : {concert.dateTime.strftime('%d %B %Y')}")
            print(f"Quantity   : {item.quantity}")
            print("-" * 30)
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def tiket_saya(user):
    """Menampilkan tiket digital dari pesanan yang sudah dibayar."""
    print_header("TIKET SAYA")
    try:
        orders = OrderService.get_orders_by_user(user.userId)
        paid_orders = [o for o in orders if o.status == "paid"]

        if not paid_orders:
            print("Belum ada tiket yang dibayar.")
        else:
            for o in paid_orders:
                concert = ConcertService.get_concert_by_id(o.concertId)
                items = OrderItem.get_by_order(o.orderId)
                for item in items:
                    ticket = TicketService.get_ticket_by_id(item.ticketId)
                    print(f"🎫 KODE: {item.itemId}")
                    print(f"   Konser  : {concert.title}")
                    print(f"   Kategori: {ticket.category}")
                    print(f"   Jumlah  : {item.quantity}")
                    print(f"   Status  : {'Digunakan' if hasattr(item, 'status') and item.status == 'used' else 'Valid'}")
                    print()
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def riwayat_pesanan(user):
    """Menampilkan riwayat pesanan user."""
    print_header("RIWAYAT PESANAN")
    try:
        orders = OrderService.get_orders_by_user(user.userId)
        if not orders:
            print("Belum ada pesanan.")
        else:
            for i, o in enumerate(orders, 1):
                concert = ConcertService.get_concert_by_id(o.concertId)
                print(f"[{i}] {o.orderId}")
                print(f"    Konser : {concert.title}")
                print(f"    Total  : Rp{o.totalAmount:,.0f}")
                print(f"    Status : {o.status.upper()}")
                print()
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def batalkan_pesanan(user):
    """Membatalkan pesanan yang masih pending."""
    print_header("BATALKAN PESANAN")
    try:
        o = _pilih_pesanan(user, "pending")
        if not o:
            pause()
            return

        yakin = input("Yakin batalkan? (y/n): ").strip().lower()
        if yakin == 'y':
            OrderService.cancel_order(o.orderId)
            print("\n[✓] Pesanan berhasil dibatalkan. Kuota tiket dikembalikan.")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


# ── IMPLEMENTASI FITUR ADMIN ────────────────────────────

def tambah_konser():
    """Admin: Menambah konser baru."""
    print_header("TAMBAH KONSER BARU")
    try:
        title = input("Judul konser         : ").strip()
        artists_str = input("Artis (pisah koma)   : ").strip()
        artistLineup = [a.strip() for a in artists_str.split(",") if a.strip()]
        venueName = input("Nama venue           : ").strip()
        venueAddress = input("Alamat venue         : ").strip()
        dateTimeStr = input("Tanggal (YYYY-MM-DD HH:MM): ").strip()
        genre = input("Genre                : ").strip()

        concert = ConcertService.create_concert({
            "title": title,
            "artistLineup": artistLineup,
            "venueName": venueName,
            "venueAddress": venueAddress,
            "dateTime": dateTimeStr,
            "genre": genre,
            "status": "upcoming"
        })
        print(f"\n[✓] Konser '{concert.title}' berhasil ditambahkan!")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def tambah_tiket():
    """Admin: Menambah tiket untuk konser tertentu."""
    print_header("TAMBAH TIKET")
    try:
        c = _pilih_konser()
        if not c:
            pause()
            return

        category = input("Kategori (VIP/REG): ").strip().upper()
        
        try:
            price = float(input("Harga tiket       : "))
            totalQuota = int(input("Total kuota       : "))
        except ValueError:
            print("\n[!] Input harga atau kuota tidak valid (harus angka).")
            pause()
            return

        ticket = TicketService.create_ticket({
            "concertId": c.concertId,
            "category": category,
            "price": price,
            "totalQuota": totalQuota,
            "remainingQuota": totalQuota
        })
        print(f"\n[✓] Tiket {ticket.category} berhasil ditambahkan!")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def lihat_semua_order():
    """Admin: Melihat semua pesanan di sistem."""
    print_header("SEMUA ORDER")
    try:
        orders = OrderService.get_all_orders()
        if not orders:
            print("Belum ada order dalam sistem.")
        for o in orders:
            print(f"Order ID : {o.orderId}")
            print(f"User ID  : {o.userId}")
            print(f"Total    : Rp{o.totalAmount:,.0f}")
            print(f"Status   : {o.status.upper()}")
            print()
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def validasi_tiket():
    """Admin: Memvalidasi tiket saat di venue."""
    print_header("VALIDASI TIKET DI VENUE")
    try:
        kode = input("Masukkan kode tiket (Item ID): ").strip()

        # Validasi dengan update status langsung di JSON order_items.json
        items_data = JsonRepository.find_all("order_items.json")
        found = False
        for i, item in enumerate(items_data):
            if item.get("itemId") == kode:
                found = True
                if item.get("status") == "used":
                    print("\n[✗] Tiket SUDAH DIGUNAKAN (INVALID).")
                else:
                    item["status"] = "used"
                    items_data[i] = item
                    JsonRepository.save("order_items.json", items_data)
                    print("\n[✓] Tiket VALID. Berhasil divalidasi dan ditandai 'used'.")
                break

        if not found:
            print("\n[✗] Kode tiket tidak ditemukan.")
    except Exception as e:
        print(f"\n[✗] Terjadi kesalahan: {e}")
    pause()


def lihat_statistik():
    """Admin: Melihat statistik umum sistem."""
    print_header("STATISTIK SISTEM")
    try:
        u_stats = UserService.get_statistics()
        o_stats = OrderService.get_statistics()
        t_stats = TicketService.get_statistics()

        print(f"Total User      : {u_stats['total_users']} (Cust: {u_stats['total_customers']}, Admin: {u_stats['total_admins']})")
        print(f"Order Pending   : {o_stats['pending']}")
        print(f"Order Paid      : {o_stats['paid']}")
        print(f"Order Cancelled : {o_stats['cancelled']}")
        print(f"Tiket Terjual   : {t_stats['tickets_sold']}")
        print(f"Total Revenue   : Rp{o_stats['total_revenue']:,.0f}")
    except Exception as e:
        print(f"\n[✗] {e}")
    pause()


if __name__ == "__main__":
    try:
        menu_utama()
    except KeyboardInterrupt:
        print("\n\n[i] Aplikasi dihentikan pengguna.")
        sys.exit(0)
