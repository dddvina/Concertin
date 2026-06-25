"""
Service Order untuk aplikasi ConcertIn.
Menyembunyikan kompleksitas pembuatan order dan relasi komposisi.
"""

from models.order import Order
from models.order_item import OrderItem
from repositories.json_repository import JsonRepository
from services.ticket_service import TicketService
from utils.exceptions import ConcertInException, OrderNotFoundException


class OrderService:
    """Layer service untuk entitas Order."""

    @staticmethod
    def create_order(user_id, concert_id, ticket_id, quantity):
        try:
            # Reserve tiket terlebih dahulu
            TicketService.reserve_ticket(ticket_id, quantity)

            # Hitung subtotal via polymorphism
            dummy_item = OrderItem(ticketId=ticket_id, quantity=quantity)
            subtotal = dummy_item.calcSubtotal()

            # Buat Order
            order = Order.create({
                "userId": user_id,
                "concertId": concert_id,
                "totalAmount": subtotal,
                "status": "pending"
            })

            # Buat OrderItem (Komposisi)
            OrderItem.create({
                "orderId": order.orderId,
                "ticketId": ticket_id,
                "quantity": quantity,
                "subTotal": subtotal
            })

            return order
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal membuat order: {e}")

    @staticmethod
    def cancel_order(order_id):
        try:
            data = JsonRepository.find_by_id(
                "orders.json", "orderId", order_id
            )
            if not data:
                raise OrderNotFoundException()

            order = Order.from_dict(data)
            if order.status == "cancelled":
                raise ConcertInException("Order sudah dibatalkan.")
            if order.status == "paid":
                raise ConcertInException(
                    "Order yang sudah dibayar tidak dapat dibatalkan."
                )

            order.cancelOrder()
            return order
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal membatalkan order: {e}")

    @staticmethod
    def get_orders_by_user(user_id):
        try:
            return Order().getByUser(user_id)
        except Exception as e:
            raise ConcertInException(f"Gagal mengambil order: {e}")

    @staticmethod
    def get_all_orders():
        try:
            all_data = JsonRepository.find_all("orders.json")
            return [Order.from_dict(d) for d in all_data]
        except Exception as e:
            raise ConcertInException(f"Gagal mengambil semua order: {e}")

    @staticmethod
    def get_order_by_id(order_id):
        data = JsonRepository.find_by_id("orders.json", "orderId", order_id)
        if not data:
            raise OrderNotFoundException()
        return Order.from_dict(data)

    @staticmethod
    def get_statistics():
        return {
            "pending": Order.count_by_status("pending"),
            "paid": Order.count_by_status("paid"),
            "cancelled": Order.count_by_status("cancelled"),
            "total_revenue": Order.total_revenue()
        }
