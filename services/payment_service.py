"""
Service Payment untuk aplikasi ConcertIn.
"""

from models.payment import Payment
from utils.exceptions import ConcertInException, OrderNotFoundException, PaymentFailedException


class PaymentService:
    """Layer service untuk entitas Payment."""

    @staticmethod
    def process_payment(order_id, method):
        try:
            from repositories.json_repository import JsonRepository
            order_data = JsonRepository.find_by_id("orders.json", "orderId", order_id)
            if not order_data:
                raise OrderNotFoundException()
            if order_data.get("status") != "pending":
                raise ConcertInException("Hanya order pending yang bisa dibayar.")

            amount = float(order_data.get("totalAmount", 0))

            # Komposisi: Buat Payment terkait Order
            payment = Payment(
                orderId=order_id,
                Method=method,
                amount=amount,
                status="pending"
            )
            payment.initiatePayment()

            # Polymorphism: Verifikasi
            if payment.verifyPayment():
                payment.handleCallback({"status": "success"})
                return payment
            else:
                payment.handleCallback({"status": "failed"})
                raise PaymentFailedException()
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal memproses pembayaran: {e}")
