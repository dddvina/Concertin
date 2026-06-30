"""
Model Payment untuk aplikasi ConcertIn.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator
from utils.exceptions import PaymentFailedException

if TYPE_CHECKING:
    from models.order import Order

DB_FILE = "payments.json"


class Payment(BaseModel):

    def __init__(self, paymentId: Optional[str] = None, order: Optional['Order'] = None, Method: str = "transfer",
                 amount: float = 0.0, status: str = "pending", paymentTime=None, created_at=None):
        super().__init__(id=paymentId, created_at=created_at)
        self.__paymentId = self.id
        self.__order = order # Komposisi dari Order (atau asosiasi dua arah)
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
    def order(self):
        return self.__order

    @order.setter
    def order(self, value):
        self.__order = value

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
        if not self.__order:
            raise ValueError("Validasi gagal: Payment harus memiliki objek Order.")
        Validator.validate_enum(self.__Method, ["transfer", "ewallet", "qris"], "Method")
        Validator.validate_positive_number(self.__amount, "amount")
        Validator.validate_enum(self.__status, ["pending", "success", "failed"], "status")

    def to_dict(self):
        return {
            "paymentId": self.__paymentId,
            "orderId": self.__order.orderId if self.__order else "",
            "Method": self.__Method,
            "amount": self.__amount,
            "status": self.__status,
            "paymentTime": self.__paymentTime.isoformat(),
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        from models.order import Order
        
        # In a real ORM we would load the order, but to prevent recursion loops
        # if Order also loads payment, we can leave it to be set.
        # But per requirements we should try to load it.
        order_data = JsonRepository.find_by_id("orders.json", "orderId", data.get("orderId"))
        order = Order.from_dict(order_data) if order_data else None
        
        return Payment(
            paymentId=data.get("paymentId"),
            order=order,
            Method=data.get("Method", "transfer"),
            amount=data.get("amount", 0.0),
            status=data.get("status", "pending"),
            paymentTime=data.get("paymentTime"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        o_id = self.__order.orderId if self.__order else "Unknown"
        return (f"Payment(id={self.__paymentId}, order={o_id}, "
                f"method={self.__Method}, amount=Rp{self.__amount:,.0f}, "
                f"status={self.__status})")

    def initiatePayment(self):
        self.__status = "pending"
        self.__paymentTime = datetime.now()
        self.validate()
        JsonRepository.insert(DB_FILE, self.to_dict())

    def verifyPayment(self):
        if self.__amount <= 0:
            raise PaymentFailedException("Jumlah pembayaran tidak valid.")
        self.__status = "success"
        self.__paymentTime = datetime.now()
        JsonRepository.update(DB_FILE, "paymentId", self.__paymentId, self.to_dict())
        return True

    def handleCallback(self, data):
        new_status = data.get("status", "failed")
        self.__status = new_status
        JsonRepository.update(DB_FILE, "paymentId", self.__paymentId, self.to_dict())

        if new_status == "success" and self.__order:
            self.__order.status = "paid"
            JsonRepository.update("orders.json", "orderId", self.__order.orderId, self.__order.to_dict())

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
        from models.order import Order
        order_data = JsonRepository.find_by_id("orders.json", "orderId", data_dict.get("orderId"))
        order = Order.from_dict(order_data) if order_data else None
        
        payment = cls(
            order=order,
            Method=data_dict.get("Method", "transfer"),
            amount=data_dict.get("amount", 0.0),
            status=data_dict.get("status", "pending")
        )
        payment.validate()
        JsonRepository.insert(DB_FILE, payment.to_dict())
        return payment