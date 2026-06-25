#front end

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
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title:^58}")
    print("=" * 60)


def print_separator():
    print("-" * 60)


def pause():
    input("\nTekan Enter untuk melanjutkan...")


# ── MENU UTAMA

def menu_utama():
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
    print_header("REGISTER")
    try:
        name = input("Nama lengkap  : ").strip()
        email = input("Email         : ").strip()
        password = input("Password      : ").strip()
        # Sesuai ketentuan, registrasi baru otomatis menjadi customer
        # Akun admin hanya 1 dan tidak bisa didaftarkan sembarangan
        role = "cust"

        user = UserService.register(name, email, password, role)
        print(f"\n[✓] Registrasi berhasil! Silakan login.")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


# ── MENU CUSTOMER ───────────────────────────────────────

def menu_customer(user):
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

        if pilihan == "1":
            lihat_semua_konser()
        elif pilihan == "2":
            cari_konser()
        elif pilihan == "3":
            detail_konser()
        elif pilihan == "4":
            pesan_tiket(user)
        elif pilihan == "5":
            bayar_pesanan(user)
        elif pilihan == "6":
            tiket_saya(user)
        elif pilihan == "7":
            riwayat_pesanan(user)
        elif pilihan == "8":
            batalkan_pesanan(user)
        elif pilihan == "0":
            user.logout()
            print("\n[✓] Logout berhasil.")
            pause()
            return
        else:
            print("\n[!] Pilihan tidak valid.")
            pause()


# ── MENU ADMIN ──────────────────────────────────────────

def menu_admin(user):
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

        if pilihan == "1":
            lihat_semua_konser()
        elif pilihan == "2":
            cari_konser()
        elif pilihan == "3":
            detail_konser()
        elif pilihan == "4":
            pesan_tiket(user)
        elif pilihan == "5":
            bayar_pesanan(user)
        elif pilihan == "6":
            tiket_saya(user)
        elif pilihan == "7":
            riwayat_pesanan(user)
        elif pilihan == "8":
            batalkan_pesanan(user)
        elif pilihan == "9":
            tambah_konser()
        elif pilihan == "10":
            tambah_tiket()
        elif pilihan == "11":
            lihat_semua_order()
        elif pilihan == "12":
            validasi_tiket()
        elif pilihan == "13":
            lihat_statistik()
        elif pilihan == "0":
            user.logout()
            print("\n[✓] Logout berhasil.")
            pause()
            return
        else:
            print("\n[!] Pilihan tidak valid.")
            pause()


# ── IMPLEMENTASI FITUR CUSTOMER ─────────────────────────

def lihat_semua_konser():
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


def detail_konser():
    print_header("DETAIL KONSER")
    try:
        concerts = ConcertService.get_all_concerts()
        for i, c in enumerate(concerts, 1):
            print(f"[{i}] {c.title}")

        idx = int(input("\nPilih nomor konser: ")) - 1
        c = concerts[idx]
        
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
    except Exception:
        print("\n[!] Input tidak valid atau terjadi kesalahan.")
    pause()


def pesan_tiket(user):
    print_header("PESAN TIKET")
    try:
        concerts = ConcertService.get_all_concerts()
        for i, c in enumerate(concerts, 1):
            print(f"[{i}] {c.title}")

        idx = int(input("\nPilih konser: ")) - 1
        c = concerts[idx]

        tickets = TicketService.get_tickets_by_concert(c.concertId)
        if not tickets:
            print("\nBelum ada tiket untuk konser ini.")
            pause()
            return

        print("\nKategori Tiket:")
        for i, t in enumerate(tickets, 1):
            print(f"[{i}] {t.category} (Rp{t.price:,.0f}) - Sisa: {t.remainingQuota}")

        t_idx = int(input("Pilih kategori: ")) - 1
        t = tickets[t_idx]

        qty = int(input("Jumlah tiket  : "))

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
    except Exception:
        print("\n[!] Terjadi kesalahan input.")
    pause()


def bayar_pesanan(user):
    print_header("BAYAR PESANAN")
    try:
        orders = OrderService.get_orders_by_user(user.userId)
        pending = [o for o in orders if o.status == "pending"]

        if not pending:
            print("Tidak ada pesanan pending.")
            pause()
            return

        for i, o in enumerate(pending, 1):
            print(f"[{i}] Order ID: {o.orderId} | Total: Rp{o.totalAmount:,.0f}")

        idx = int(input("\nPilih pesanan: ")) - 1
        o = pending[idx]

        print("\nMetode Pembayaran:")
        print("1. Transfer Bank\n2. E-Wallet\n3. QRIS")
        m_idx = input("Pilih metode: ")
        metode = {"1": "transfer", "2": "ewallet", "3": "qris"}.get(m_idx)

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
    except Exception:
        print("\n[!] Terjadi kesalahan input.")
    pause()


def tiket_saya(user):
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
                    # Ambil informasi tiket
                    ticket = TicketService.get_ticket_by_id(item.ticketId)
                    
                    print(f"🎫 KODE: {item.itemId}")
                    print(f"   Konser  : {concert.title}")
                    print(f"   Kategori: {ticket.category}")
                    print(f"   Jumlah  : {item.quantity}")
                    print(f"   Status  : Valid")
                    print()
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    pause()


def riwayat_pesanan(user):
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
    print_header("BATALKAN PESANAN")
    try:
        orders = OrderService.get_orders_by_user(user.userId)
        pending = [o for o in orders if o.status == "pending"]

        if not pending:
            print("Tidak ada pesanan pending.")
            pause()
            return

        for i, o in enumerate(pending, 1):
            print(f"[{i}] Order ID: {o.orderId} | Total: Rp{o.totalAmount:,.0f}")

        idx = int(input("\nPilih pesanan yang akan dibatalkan: ")) - 1
        o = pending[idx]

        yakin = input("Yakin batalkan? (y/n): ").lower()
        if yakin == 'y':
            OrderService.cancel_order(o.orderId)
            print("\n[✓] Pesanan berhasil dibatalkan. Kuota tiket dikembalikan.")
    except ConcertInException as e:
        print(f"\n[✗] {e}")
    except Exception:
        print("\n[!] Input tidak valid.")
    pause()


# ── IMPLEMENTASI FITUR ADMIN ────────────────────────────

def tambah_konser():
    print_header("TAMBAH KONSER BARU")
    try:
        title = input("Judul konser         : ").strip()
        artists_str = input("Artis (pisah koma)   : ").strip()
        artistLineup = [a.strip() for a in artists_str.split(",")]
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
    print_header("TAMBAH TIKET")
    try:
        concerts = ConcertService.get_all_concerts()
        for i, c in enumerate(concerts, 1):
            print(f"[{i}] {c.title}")

        idx = int(input("\nPilih konser: ")) - 1
        c = concerts[idx]

        category = input("Kategori (VIP/REG): ").upper()
        price = float(input("Harga tiket       : "))
        totalQuota = int(input("Total kuota       : "))

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
    except Exception:
        print("\n[!] Input tidak valid.")
    pause()


def lihat_semua_order():
    print_header("SEMUA ORDER")
    try:
        orders = OrderService.get_all_orders()
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
    menu_utama()

#aaa