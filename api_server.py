"""
API Server untuk menghubungkan Frontend (HTML/JS) ke Backend (Python).
Menyediakan static file server dan JSON API endpoints.
"""

import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Tambahkan direktori root ke sys.path agar bisa import models & services
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService
from services.concert_service import ConcertService
from services.ticket_service import TicketService
from services.order_service import OrderService
from utils.exceptions import ConcertInException

FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'frontend'
)


class APIHandler(SimpleHTTPRequestHandler):
    """Handler HTTP untuk API endpoints dan static file serving."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _send_json(self, status_code, data):
        """Helper untuk mengirim response JSON."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _read_body(self):
        """Helper: baca dan parse request body JSON."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length <= 0:
            return {}
        try:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    # ── GET Endpoints ──────────────────────────────────────

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/concerts':
            self._handle_get_concerts()
        elif path == '/api/tickets':
            query = parse_qs(parsed.query)
            concert_id = query.get('concertId', [None])[0]
            self._handle_get_tickets(concert_id)
        else:
            # Fallback melayani file statis (HTML/CSS/JS)
            super().do_GET()

    def _handle_get_concerts(self):
        try:
            concerts = ConcertService.get_all_concerts()
            data = [c.to_dict() for c in concerts]
            self._send_json(200, {"success": True, "data": data})
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    def _handle_get_tickets(self, concert_id):
        if not concert_id:
            self._send_json(
                400, {"success": False, "message": "concertId required"}
            )
            return
        try:
            tickets = TicketService.get_tickets_by_concert(concert_id)
            data = [t.to_dict() for t in tickets]
            self._send_json(200, {"success": True, "data": data})
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    # ── POST Endpoints ─────────────────────────────────────

    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        req_data = self._read_body()

        handlers = {
            '/api/login': self._handle_login,
            '/api/register': self._handle_register,
            '/api/admin/register': self._handle_admin_register,
            '/api/orders': self._handle_create_order,
        }

        handler = handlers.get(path)
        if handler:
            handler(req_data)
        else:
            self._send_json(
                404, {"success": False, "message": "Endpoint not found"}
            )

    def _handle_login(self, req_data):
        try:
            user = UserService.login(
                req_data.get("email"), req_data.get("password")
            )
            self._send_json(200, {"success": True, "data": user.to_dict()})
        except ConcertInException as e:
            self._send_json(401, {"success": False, "message": str(e)})
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    def _handle_register(self, req_data):
        try:
            user = UserService.register(
                req_data.get("name"),
                req_data.get("email"),
                req_data.get("password"),
                "cust"  # Memaksa role customer sesuai ketentuan keamanan
            )
            self._send_json(200, {"success": True, "data": user.to_dict()})
        except ConcertInException as e:
            self._send_json(400, {"success": False, "message": str(e)})
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    def _handle_admin_register(self, req_data):
        try:
            user = UserService.register(
                req_data.get("name"),
                req_data.get("email"),
                req_data.get("password"),
                req_data.get("role", "admin")
            )
            self._send_json(200, {"success": True, "data": user.to_dict()})
        except ConcertInException as e:
            self._send_json(400, {"success": False, "message": str(e)})
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})

    def _handle_create_order(self, req_data):
        try:
            order = OrderService.create_order(
                req_data.get("userId"),
                req_data.get("concertId"),
                req_data.get("ticketId"),
                int(req_data.get("quantity", 0))
            )
            self._send_json(200, {"success": True, "data": order.to_dict()})
        except ConcertInException as e:
            self._send_json(400, {"success": False, "message": str(e)})
        except Exception as e:
            self._send_json(500, {"success": False, "message": str(e)})


def run(port=8000):
    """Start the ConcertIn API server."""
    server = HTTPServer(('', port), APIHandler)
    print(f"========================================")
    print(f"🚀 ConcertIn API Server & Frontend aktif")
    print(f"👉 Buka browser di: http://localhost:{port}")
    print(f"========================================")
    print("Tekan Ctrl+C untuk menghentikan server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("\nServer dihentikan.")


if __name__ == '__main__':
    run()
