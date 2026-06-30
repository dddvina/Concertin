"""
API Server untuk aplikasi ConcertIn.
Menyediakan RESTful endpoint yang menghubungkan frontend dengan backend OOP.
Menggunakan built-in http.server agar tidak perlu dependency eksternal.
"""

import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Pastikan root project ada di sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService
from services.concert_service import ConcertService
from services.ticket_service import TicketService
from services.order_service import OrderService
from services.payment_service import PaymentService
from utils.exceptions import ConcertInException, UnauthorizedException


class APIRequestHandler(SimpleHTTPRequestHandler):

    # Map folder frontend sebagai root untuk file statis
    FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.FRONTEND_DIR, **kwargs)

    # ── Helper Response ──────────────────────────────────────

    def _send_json(self, data, status=200):
        """Kirim response JSON dengan status code yang sesuai."""
        response_body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_body)

    def _read_body(self):
        """Baca dan parse body JSON dari request."""
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        return json.loads(raw) if raw else {}

    # ── CORS Preflight ───────────────────────────────────────

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── GET Requests ─────────────────────────────────────────

    def do_GET(self):
        """Route GET requests ke API handler atau file statis."""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        try:
            if path == "/api/concerts":
                self._handle_get_concerts(params)
            elif path == "/api/concerts/search":
                self._handle_search_concerts(params)
            elif path.startswith("/api/concerts/"):
                concert_id = path.split("/api/concerts/")[1]
                self._handle_get_concert_detail(concert_id)
            elif path.startswith("/api/tickets/concert/"):
                concert_id = path.split("/api/tickets/concert/")[1]
                self._handle_get_tickets_by_concert(concert_id)
            elif path.startswith("/api/orders/user/"):
                user_id = path.split("/api/orders/user/")[1]
                self._handle_get_orders_by_user(user_id)
            elif path == "/api/orders":
                self._handle_get_all_orders(params)
            elif path == "/api/statistics":
                self._handle_get_statistics()
            else:
                # Serve file statis dari folder frontend
                super().do_GET()
        except UnauthorizedException as e:
            self._send_json({"success": False, "error": str(e)}, 403)
        except ConcertInException as e:
            self._send_json({"success": False, "error": str(e)}, 400)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    # ── POST Requests ────────────────────────────────────────

    def do_POST(self):
        """Route POST requests ke API handler yang sesuai."""
        path = urlparse(self.path).path

        try:
            body = self._read_body()

            if path == "/api/auth/login":
                self._handle_login(body)
            elif path == "/api/auth/register":
                self._handle_register(body)
            elif path == "/api/orders":
                self._handle_create_order(body)
            elif path == "/api/payments":
                self._handle_process_payment(body)
            elif path == "/api/orders/cancel":
                self._handle_cancel_order(body)
            elif path == "/api/concerts":
                self._handle_create_concert(body)
            elif path == "/api/tickets":
                self._handle_create_ticket(body)
            elif path == "/api/tickets/validate":
                self._handle_validate_ticket(body)
            else:
                self._send_json({"success": False, "error": "Endpoint tidak ditemukan."}, 404)
        except UnauthorizedException as e:
            self._send_json({"success": False, "error": str(e)}, 403)
        except ConcertInException as e:
            self._send_json({"success": False, "error": str(e)}, 400)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    # ── Auth Handlers ────────────────────────────────────────

    def _handle_login(self, body):
        """Proses login user, kembalikan data user jika berhasil."""
        email = body.get("email", "")
        password = body.get("password", "")
        user = UserService.login(email, password)
        self._send_json({
            "success": True,
            "user": user.to_dict()
        })

    def _handle_register(self, body):
        """Proses registrasi user baru."""
        user = UserService.register(
            name=body.get("name", ""),
            email=body.get("email", ""),
            password=body.get("password", ""),
            role="cust"
        )
        self._send_json({
            "success": True,
            "message": "Registrasi berhasil! Silakan login.",
            "user": user.to_dict()
        })

    # ── Concert Handlers ─────────────────────────────────────

    def _handle_get_concerts(self, params):
        """Ambil semua konser, dikembalikan sebagai JSON array."""
        concerts = ConcertService.get_all_concerts()
        result = []
        for c in concerts:
            c_dict = c.to_dict()
            tickets = TicketService.get_tickets_by_concert(c.concertId)
            c_dict["tickets"] = [t.to_dict() for t in tickets]
            min_price = min((t.price for t in tickets), default=0)
            total_slots = sum(t.remainingQuota for t in tickets)
            c_dict["minPrice"] = min_price
            c_dict["totalSlots"] = total_slots
            result.append(c_dict)
        self._send_json({"success": True, "concerts": result})

    def _handle_search_concerts(self, params):
        """Cari konser berdasarkan keyword."""
        keyword = params.get("q", [""])[0]
        concerts = ConcertService.search_concerts(keyword)
        result = []
        for c in concerts:
            c_dict = c.to_dict()
            tickets = TicketService.get_tickets_by_concert(c.concertId)
            c_dict["tickets"] = [t.to_dict() for t in tickets]
            min_price = min((t.price for t in tickets), default=0)
            total_slots = sum(t.remainingQuota for t in tickets)
            c_dict["minPrice"] = min_price
            c_dict["totalSlots"] = total_slots
            result.append(c_dict)
        self._send_json({"success": True, "concerts": result})

    def _handle_get_concert_detail(self, concert_id):
        """Ambil detail konser beserta tiket-tiketnya."""
        concert = ConcertService.get_concert_by_id(concert_id)
        c_dict = concert.to_dict()
        tickets = TicketService.get_tickets_by_concert(concert_id)
        c_dict["tickets"] = [t.to_dict() for t in tickets]
        self._send_json({"success": True, "concert": c_dict})

    def _handle_get_tickets_by_concert(self, concert_id):
        """Ambil semua tiket untuk konser tertentu."""
        tickets = TicketService.get_tickets_by_concert(concert_id)
        self._send_json({
            "success": True,
            "tickets": [t.to_dict() for t in tickets]
        })

    # ── Order Handlers ───────────────────────────────────────

    def _handle_create_order(self, body):
        """Buat order baru (harus sudah login)."""
        order = OrderService.create_order(
            user_id=body.get("userId"),
            concert_id=body.get("concertId"),
            ticket_id=body.get("ticketId"),
            quantity=int(body.get("quantity", 1))
        )
        self._send_json({
            "success": True,
            "message": "Pesanan berhasil dibuat!",
            "order": order.to_dict()
        })

    def _handle_cancel_order(self, body):
        """Batalkan order pending."""
        order = OrderService.cancel_order(body.get("orderId"))
        self._send_json({
            "success": True,
            "message": "Pesanan berhasil dibatalkan."
        })

    def _handle_get_orders_by_user(self, user_id):
        """Ambil semua order milik user tertentu."""
        orders = OrderService.get_orders_by_user(user_id)
        result = []
        for o in orders:
            o_dict = o.to_dict()
            try:
                concert = ConcertService.get_concert_by_id(o.concertId)
                o_dict["concertTitle"] = concert.title
                o_dict["concertDate"] = concert.dateTime.isoformat()
            except Exception:
                o_dict["concertTitle"] = "Konser Tidak Diketahui"
                o_dict["concertDate"] = ""
            result.append(o_dict)
        self._send_json({"success": True, "orders": result})

    def _handle_get_all_orders(self, params):
        """Ambil semua order (admin only). requesterId dikirim lewat query string."""
        requester_id = params.get("requesterId", [""])[0]
        orders = OrderService.get_all_orders(requester_id)
        self._send_json({
            "success": True,
            "orders": [o.to_dict() for o in orders]
        })

    # ── Payment Handler ──────────────────────────────────────

    def _handle_process_payment(self, body):
        """Proses pembayaran untuk order tertentu."""
        payment = PaymentService.process_payment(
            order_id=body.get("orderId"),
            method=body.get("method", "transfer")
        )
        self._send_json({
            "success": True,
            "message": "Pembayaran berhasil!",
            "payment": payment.to_dict()
        })

    # ── Admin Handlers ───────────────────────────────────────

    def _handle_create_concert(self, body):
        """Tambah konser baru (admin only). requesterId wajib dikirim di body."""
        concert = ConcertService.create_concert(body, body.get("requesterId"))
        self._send_json({
            "success": True,
            "message": "Konser berhasil ditambahkan!",
            "concert": concert.to_dict()
        })

    def _handle_create_ticket(self, body):
        """Tambah tiket untuk konser (admin only). requesterId wajib dikirim di body."""
        ticket = TicketService.create_ticket(body, body.get("requesterId"))
        self._send_json({
            "success": True,
            "message": "Tiket berhasil ditambahkan!",
            "ticket": ticket.to_dict()
        })

    def _handle_validate_ticket(self, body):
        """Validasi tiket di venue (admin only). requesterId wajib dikirim di body."""
        UserService.require_admin(body.get("requesterId"))

        from repositories.json_repository import JsonRepository
        kode = body.get("ticketCode", "")
        items_data = JsonRepository.find_all("order_items.json")

        for i, item in enumerate(items_data):
            if item.get("itemId") == kode:
                if item.get("status") == "used":
                    self._send_json({
                        "success": False,
                        "error": "Tiket sudah digunakan (INVALID)."
                    }, 400)
                    return
                item["status"] = "used"
                items_data[i] = item
                JsonRepository.save("order_items.json", items_data)
                self._send_json({
                    "success": True,
                    "message": "Tiket VALID dan berhasil divalidasi."
                })
                return

        self._send_json({
            "success": False,
            "error": "Kode tiket tidak ditemukan."
        }, 404)

    # ── Statistics Handler ───────────────────────────────────

    def _handle_get_statistics(self):
        """Ambil statistik sistem."""
        u_stats = UserService.get_statistics()
        o_stats = OrderService.get_statistics()
        t_stats = TicketService.get_statistics()
        self._send_json({
            "success": True,
            "statistics": {**u_stats, **o_stats, **t_stats}
        })

    # ── Suppress log noise ───────────────────────────────────

    def log_message(self, format, *args):
        """Override log untuk menampilkan request dengan format lebih bersih."""
        sys.stdout.write(f"[API] {args[0]}\n")


def run_server(host="127.0.0.1", port=8080):
    """Jalankan server HTTP ConcertIn."""
    server = HTTPServer((host, port), APIRequestHandler)
    print(f"\n{'='*50}")
    print(f"  [ConcertIn] API Server")
    print(f"  - http://{host}:{port}")
    print(f"  - Serving frontend from: {APIRequestHandler.FRONTEND_DIR}")
    print(f"{'='*50}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server dihentikan.")
        server.server_close()


if __name__ == "__main__":
    run_server()