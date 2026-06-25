"""
Model Payment untuk aplikasi ConcertIn.
Merepresentasikan pembayaran dari suatu pesanan.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from datetime import datetime
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator
from utils.exceptions import PaymentFailedException

DB_FILE = "payments.json"


class Payment(BaseModel):
    """
    Model Payment merepresentasikan transaksi pembayaran.

    Attributes:
        __paymentId (str): Unique payment identifier.
        __orderId (str): ID order terkait (FK).
        __Method (str): Metode pembayaran (transfer, ewallet, qris).
        __amount (float): Jumlah pembayaran.
        __status (str): Status pembayaran (pending, success, failed).
        __paymentTime (datetime): Waktu pembayaran.
    """

    def __init__(self, paymentId=None, orderId="", Method="transfer",
                 amount=0.0, status="pending", paymentTime=None, created_at=None):
        super().__init__(id=paymentId, created_at=created_at)
        self.__paymentId = self.id
        self.__orderId = orderId
        self.__Method = Method
        self.__amount = float(amount)
        self.__status = status
        if paymentTime is None:
            self.__paymentTime = datetime.now()
        elif isinstance(paymentTime, str):
            self.__paymentTime = datetime.fromisoformat(paymentTime)
        else:
            self.__paymentTime = paymentTime

    # ── Properties ──────────────────────────────────────────

    @property
    def paymentId(self):
        return self.__paymentId

    @paymentId.setter
    def paymentId(self, value):
        self.__paymentId = value

    @property
    def orderId(self):
        return self.__orderId

    @orderId.setter
    def orderId(self, value):
        self.__orderId = value

    @property
    def Method(self):
        return self.__Method

    @Method.setter
    def Method(self, value):
        self.__Method = value

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = float(value)

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def paymentTime(self):
        return self.__paymentTime

    @paymentTime.setter
    def paymentTime(self, value):
        if isinstance(value, str):
            self.__paymentTime = datetime.fromisoformat(value)
        else:
            self.__paymentTime = value

    # ── Instance Methods ────────────────────────────────────

    def validate(self):
        Validator.validate_not_empty(self.__orderId, "orderId")
        Validator.validate_enum(self.__Method, ["transfer", "ewallet", "qris"], "Method")
        Validator.validate_positive_number(self.__amount, "amount")
        Validator.validate_enum(self.__status, ["pending", "success", "failed"], "status")

    def to_dict(self):
        return {
            "paymentId": self.__paymentId,
            "orderId": self.__orderId,
            "Method": self.__Method,
            "amount": self.__amount,
            "status": self.__status,
            "paymentTime": self.__paymentTime.isoformat(),
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return Payment(
            paymentId=data.get("paymentId"),
            orderId=data.get("orderId", ""),
            Method=data.get("Method", "transfer"),
            amount=data.get("amount", 0.0),
            status=data.get("status", "pending"),
            paymentTime=data.get("paymentTime"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        return (f"Payment(id={self.__paymentId}, order={self.__orderId}, "
                f"method={self.__Method}, amount=Rp{self.__amount:,.0f}, "
                f"status={self.__status})")

    def initiatePayment(self):
        """Inisialisasi pembayaran ke DB dengan status pending."""
        self.__status = "pending"
        self.__paymentTime = datetime.now()
        self.validate()
        JsonRepository.insert(DB_FILE, self.to_dict())

    def verifyPayment(self):
        """
        Polymorphism: Verifikasi pembayaran.
        Disimulasikan berhasil jika jumlah > 0.
        """
        if self.__amount <= 0:
            raise PaymentFailedException("Jumlah pembayaran tidak valid.")
        self.__status = "success"
        self.__paymentTime = datetime.now()
        JsonRepository.update(DB_FILE, "paymentId", self.__paymentId, self.to_dict())
        return True

    def handleCallback(self, data):
        """Handle callback untuk update status."""
        new_status = data.get("status", "failed")
        self.__status = new_status
        JsonRepository.update(DB_FILE, "paymentId", self.__paymentId, self.to_dict())

        if new_status == "success":
            order_data = JsonRepository.find_by_id("orders.json", "orderId", self.__orderId)
            if order_data:
                order_data["status"] = "paid"
                JsonRepository.update("orders.json", "orderId", self.__orderId, order_data)

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_by_status(status):
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(1 for d in all_data if d.get("status") == status)

    @staticmethod
    def total_paid():
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(float(d.get("amount", 0)) for d in all_data if d.get("status") == "success")

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        payment = cls(
            orderId=data_dict.get("orderId", ""),
            Method=data_dict.get("Method", "transfer"),
            amount=data_dict.get("amount", 0.0),
            status=data_dict.get("status", "pending")
        )
        payment.validate()
        JsonRepository.insert(DB_FILE, payment.to_dict())
        return payment
