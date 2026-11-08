# Vercel Serverless Handler — ConcertIn
# File ini menangani semua /api/* request di Vercel.
# Vercel Python runtime memanggil class `handler` yang inherit BaseHTTPRequestHandler.

import sys
import os
import json
import base64
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Path setup: agar models/services/repositories bisa diimpor ──────────────
# Di Vercel, file ini ada di /var/task/api/index.py
# Root project ada di /var/task/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.user_service import UserService
from services.concert_service import ConcertService
from services.ticket_service import TicketService
from services.order_service import OrderService
from services.payment_service import PaymentService
from utils.exceptions import ConcertInException, UnauthorizedException


class handler(BaseHTTPRequestHandler):

    # ── Helper Response ──────────────────────────────────────────────────────

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        return json.loads(raw) if raw else {}

    # ── CORS Preflight ───────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── GET ──────────────────────────────────────────────────────────────────

    def do_GET(self):
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
                self._send_json({"success": False, "error": "Endpoint tidak ditemukan."}, 404)
        except UnauthorizedException as e:
            self._send_json({"success": False, "error": str(e)}, 403)
        except ConcertInException as e:
            self._send_json({"success": False, "error": str(e)}, 400)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    # ── POST ─────────────────────────────────────────────────────────────────

    def do_POST(self):
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
            elif path == "/api/upload":
                self._handle_upload_image(body)
            else:
                self._send_json({"success": False, "error": "Endpoint tidak ditemukan."}, 404)
        except UnauthorizedException as e:
            self._send_json({"success": False, "error": str(e)}, 403)
        except ConcertInException as e:
            self._send_json({"success": False, "error": str(e)}, 400)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    # ── DELETE ───────────────────────────────────────────────────────────────

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        try:
            if path.startswith("/api/concerts/"):
                concert_id = path.split("/api/concerts/")[1]
                requester_id = params.get("requesterId", [""])[0]
                self._handle_delete_concert(concert_id, requester_id)
            else:
                self._send_json({"success": False, "error": "Endpoint tidak ditemukan."}, 404)
        except UnauthorizedException as e:
            self._send_json({"success": False, "error": str(e)}, 403)
        except ConcertInException as e:
            self._send_json({"success": False, "error": str(e)}, 400)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    # ── Auth Handlers ────────────────────────────────────────────────────────

    def _handle_login(self, body):
        email = body.get("email", "")
        password = body.get("password", "")
        user = UserService.login(email, password)
        self._send_json({"success": True, "user": user.to_dict()})

    def _handle_register(self, body):
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

    # ── Concert Handlers ─────────────────────────────────────────────────────

    def _handle_get_concerts(self, params):
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
        concert = ConcertService.get_concert_by_id(concert_id)
        c_dict = concert.to_dict()
        tickets = TicketService.get_tickets_by_concert(concert_id)
        c_dict["tickets"] = [t.to_dict() for t in tickets]
        self._send_json({"success": True, "concert": c_dict})

    def _handle_get_tickets_by_concert(self, concert_id):
        tickets = TicketService.get_tickets_by_concert(concert_id)
        self._send_json({"success": True, "tickets": [t.to_dict() for t in tickets]})

    # ── Order Handlers ───────────────────────────────────────────────────────

    def _handle_create_order(self, body):
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
        OrderService.cancel_order(body.get("orderId"))
        self._send_json({"success": True, "message": "Pesanan berhasil dibatalkan."})

    def _handle_get_orders_by_user(self, user_id):
        orders = OrderService.get_orders_by_user(user_id)
        result = []
        for o in orders:
            o_dict = o.to_dict()
            try:
                if o.concert:
                    o_dict["concertTitle"] = o.concert.title
                    o_dict["concertDate"] = o.concert.dateTime.isoformat()
                else:
                    raise Exception("Concert not found")
            except Exception:
                o_dict["concertTitle"] = "Konser Tidak Diketahui"
                o_dict["concertDate"] = ""
            result.append(o_dict)
        self._send_json({"success": True, "orders": result})

    def _handle_get_all_orders(self, params):
        requester_id = params.get("requesterId", [""])[0]
        orders = OrderService.get_all_orders(requester_id)
        self._send_json({"success": True, "orders": [o.to_dict() for o in orders]})

    # ── Payment Handler ──────────────────────────────────────────────────────

    def _handle_process_payment(self, body):
        payment = PaymentService.process_payment(
            order_id=body.get("orderId"),
            method=body.get("method", "transfer")
        )
        self._send_json({
            "success": True,
            "message": "Pembayaran berhasil!",
            "payment": payment.to_dict()
        })

    # ── Admin Handlers ───────────────────────────────────────────────────────

    def _handle_create_concert(self, body):
        concert = ConcertService.create_concert(body, body.get("requesterId"))
        self._send_json({
            "success": True,
            "message": "Konser berhasil ditambahkan!",
            "concert": concert.to_dict()
        })

    def _handle_upload_image(self, body):
        """Decode base64 image dan simpan ke /tmp/ (Vercel ephemeral storage)."""
        base64_data = body.get("base64", "")
        ext = body.get("ext", "jpg").lower()

        allowed = {"jpg", "jpeg", "png", "webp", "gif"}
        if ext not in allowed:
            self._send_json({"success": False, "error": "Format file tidak didukung."}, 400)
            return

        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(base64_data)
        except Exception:
            self._send_json({"success": False, "error": "Data gambar tidak valid."}, 400)
            return

        if len(image_bytes) > 5 * 1024 * 1024:
            self._send_json({"success": False, "error": "Ukuran gambar melebihi 5 MB."}, 400)
            return

        filename = f"{uuid.uuid4().hex}.{ext}"
        # Di Vercel, hanya /tmp yang bisa ditulis (ephemeral)
        save_path = os.path.join("/tmp", filename)
        with open(save_path, "wb") as f:
            f.write(image_bytes)

        # Return URL relatif — gambar tidak akan persisten di Vercel
        self._send_json({
            "success": True,
            "imageUrl": f"assets/{filename}",
            "note": "Gambar bersifat sementara di Vercel."
        })

    def _handle_delete_concert(self, concert_id, requester_id):
        deleted = ConcertService.delete_concert(concert_id, requester_id)
        self._send_json({
            "success": True,
            "message": f"Konser '{deleted.title}' berhasil dihapus!"
        })

    def _handle_create_ticket(self, body):
        ticket = TicketService.create_ticket(body, body.get("requesterId"))
        self._send_json({
            "success": True,
            "message": "Tiket berhasil ditambahkan!",
            "ticket": ticket.to_dict()
        })

    def _handle_validate_ticket(self, body):
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

        self._send_json({"success": False, "error": "Kode tiket tidak ditemukan."}, 404)

    # ── Statistics Handler ───────────────────────────────────────────────────

    def _handle_get_statistics(self):
        u_stats = UserService.get_statistics()
        o_stats = OrderService.get_statistics()
        t_stats = TicketService.get_statistics()
        self._send_json({
            "success": True,
            "statistics": {**u_stats, **o_stats, **t_stats}
        })

    def log_message(self, format, *args):
        pass  # Suppress log noise di Vercel
