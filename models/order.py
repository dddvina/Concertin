"""
Model Order untuk aplikasi ConcertIn.
Merepresentasikan pesanan tiket oleh user.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from datetime import datetime
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator

DB_FILE = "orders.json"


class Order(BaseModel):

    def __init__(self, orderId=None, userId="", concertId="", totalAmount=0.0,
                 orderDate=None, status="pending", created_at=None):
        super().__init__(id=orderId, created_at=created_at)
        self.__orderId = self.id
        self.__userId = userId
        self.__concertId = concertId
        self.__totalAmount = float(totalAmount)
        if orderDate is None:
            self.__orderDate = datetime.now()
        elif isinstance(orderDate, str):
            self.__orderDate = datetime.fromisoformat(orderDate)
        else:
            self.__orderDate = orderDate
        self.__status = status
        self.__user = None
        self.__concert = None
        self.__orderItems = []

    # ── Properties ──────────────────────────────────────────

    @property
    def orderId(self):
        return self.__orderId

    @orderId.setter
    def orderId(self, value):
        self.__orderId = value

    @property
    def userId(self):
        return self.__userId

    @userId.setter
    def userId(self, value):
        self.__userId = value

    @property
    def concertId(self):
        return self.__concertId

    @concertId.setter
    def concertId(self, value):
        self.__concertId = value

    @property
    def totalAmount(self):
        return self.__totalAmount

    @totalAmount.setter
    def totalAmount(self, value):
        self.__totalAmount = float(value)

    @property
    def orderDate(self):
        return self.__orderDate

    @orderDate.setter
    def orderDate(self, value):
        if isinstance(value, str):
            self.__orderDate = datetime.fromisoformat(value)
        else:
            self.__orderDate = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    # ── Instance Methods ────────────────────────────────────

    def validate(self):
        Validator.validate_not_empty(self.__userId, "userId")
        Validator.validate_not_empty(self.__concertId, "concertId")
        Validator.validate_enum(self.__status, ["pending", "paid", "cancelled"], "status")

    def to_dict(self):
        return {
            "orderId": self.__orderId,
            "userId": self.__userId,
            "concertId": self.__concertId,
            "totalAmount": self.__totalAmount,
            "orderDate": self.__orderDate.isoformat(),
            "status": self.__status,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return Order(
            orderId=data.get("orderId"),
            userId=data.get("userId", ""),
            concertId=data.get("concertId", ""),
            totalAmount=data.get("totalAmount", 0.0),
            orderDate=data.get("orderDate"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        return (f"Order(id={self.__orderId}, user={self.__userId}, "
                f"total=Rp{self.__totalAmount:,.0f}, status={self.__status})")

    def loadUser(self):
        from models.user import User
        user_data = JsonRepository.find_by_id("users.json", "userId", self.__userId)
        self.__user = User.from_dict(user_data) if user_data else None
        return self.__user

    def loadConcert(self):
        from models.concert import Concert
        concert = Concert().getById(self.__concertId)
        self.__concert = concert
        return concert

    def loadOrderItems(self):
        """Ambil semua object OrderItem yang menjadi bagian dari order ini."""
        from models.order_item import OrderItem
        self.__orderItems = OrderItem.get_by_order(self.__orderId)
        return self.__orderItems

    def createOrder(self):
        """Validasi user & concert terkait lewat object masing-masing, lalu simpan order."""
        self.validate()

        user = self.loadUser()
        if user is None:
            raise ValueError(f"User dengan id '{self.__userId}' tidak ditemukan.")

        concert = self.loadConcert()
        if concert is None:
            raise ValueError(f"Concert dengan id '{self.__concertId}' tidak ditemukan.")
        if concert.status in ("completed", "cancelled"):
            raise ValueError(
                f"Tidak dapat membuat order untuk concert berstatus '{concert.status}'."
            )

        JsonRepository.insert(DB_FILE, self.to_dict())
        return self

    def markAsPaid(self):
        """Tandai order sebagai sudah dibayar (dipanggil oleh Payment saat sukses)."""
        self.__status = "paid"
        JsonRepository.update(DB_FILE, "orderId", self.__orderId, self.to_dict())

    def cancelOrder(self):
        """Batalkan order; kuota tiket dikembalikan lewat object OrderItem (yang lalu manggil Ticket)."""
        self.__status = "cancelled"
        JsonRepository.update(DB_FILE, "orderId", self.__orderId, self.to_dict())

        items = self.loadOrderItems()
        for item in items:
            item.releaseQuota()

    def getByUser(self, user_id):
        all_data = JsonRepository.find_all(DB_FILE)
        return [Order.from_dict(d) for d in all_data if d.get("userId") == user_id]

    def getStatus(self):
        return self.__status

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_by_status(status):
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(1 for d in all_data if d.get("status") == status)

    @staticmethod
    def total_revenue():
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(float(d.get("totalAmount", 0)) for d in all_data if d.get("status") == "paid")

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        order = cls(
            userId=data_dict.get("userId", ""),
            concertId=data_dict.get("concertId", ""),
            totalAmount=data_dict.get("totalAmount", 0.0),
            status=data_dict.get("status", "pending")
        )
        order.validate()
        JsonRepository.insert(DB_FILE, order.to_dict())
        return order