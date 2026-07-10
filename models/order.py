"""
Model Order untuk aplikasi ConcertIn.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator

if TYPE_CHECKING:
    from models.user import User
    from models.concert import Concert
    from models.order_item import OrderItem
    from models.payment import Payment

DB_FILE = "orders.json"


class Order(BaseModel):

    def __init__(self, orderId: Optional[str] = None, user: Optional['User'] = None, 
                 concert: Optional['Concert'] = None, totalAmount: float = 0.0,
                 orderDate=None, status: str = "pending", created_at=None):
        super().__init__(id=orderId, created_at=created_at)
        self.__orderId = self.id
        self.__user = user        # Asosiasi ke User
        self.__concert = concert  # Asosiasi ke Concert
        self.__totalAmount = float(totalAmount)
        
        if orderDate is None:
            self.__orderDate = datetime.now()
        elif isinstance(orderDate, str):
            self.__orderDate = datetime.fromisoformat(orderDate)
        else:
            self.__orderDate = orderDate
            
        self.__status = status
        
        # Komposisi
        self.__orderItems = []
        self.__payment = None

    # ── Properties ──────────────────────────────────────────

    @property
    def orderId(self):
        return self.__orderId

    @orderId.setter
    def orderId(self, value):
        self.__orderId = value

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        self.__user = value

    @property
    def concert(self):
        return self.__concert

    @concert.setter
    def concert(self, value):
        self.__concert = value

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

    @property
    def orderItems(self):
        return self.__orderItems
        
    @property
    def payment(self):
        return self.__payment

    # ── Instance Methods ────────────────────────────────────

    def validate(self):
        if not self.__user:
            raise ValueError("Validasi gagal: Order harus memiliki objek User.")
        if not self.__concert:
            raise ValueError("Validasi gagal: Order harus memiliki objek Concert.")
        Validator.validate_enum(self.__status, ["pending", "paid", "cancelled"], "status")

    def to_dict(self):
        return {
            "orderId": self.__orderId,
            "userId": self.__user.userId if self.__user else "",
            "concertId": self.__concert.concertId if self.__concert else "",
            "totalAmount": self.__totalAmount,
            "orderDate": self.__orderDate.isoformat(),
            "status": self.__status,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        from models.user import User #User class
        from models.concert import Concert
        
        user_data = JsonRepository.find_by_id("users.json", "userId", data.get("userId"))
        user = User.from_dict(user_data) if user_data else None
        
        concert_data = JsonRepository.find_by_id("concerts.json", "concertId", data.get("concertId"))
        concert = Concert.from_dict(concert_data) if concert_data else None
        
        return Order(
            orderId=data.get("orderId"),
            user=user,
            concert=concert,
            totalAmount=data.get("totalAmount", 0.0),
            orderDate=data.get("orderDate"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        u_name = self.__user.name if self.__user else "Unknown"
        return (f"Order(id={self.__orderId}, user={u_name}, "
                f"total=Rp{self.__totalAmount:,.0f}, status={self.__status})")

    def loadOrderItems(self):
        # OrderItem (Komposisi)
        from models.order_item import OrderItem
        self.__orderItems = OrderItem.get_by_order(self)
        return self.__orderItems
        
    def loadPayment(self):
        from models.payment import Payment #class Payment
        all_payments = JsonRepository.find_all("payments.json")
        for pd in all_payments:
            if pd.get("orderId") == self.__orderId:
                self.__payment = Payment.from_dict(pd)
                return self.__payment
        return None

    def createOrder(self): #CREATE
        self.validate()
        if self.__concert.status in ("completed", "cancelled"):
            raise ValueError(
                f"Tidak dapat membuat order untuk concert berstatus '{self.__concert.status}'."
            )
        JsonRepository.insert(DB_FILE, self.to_dict())
        return self

    def markAsPaid(self): #UPDATE
        self.__status = "paid"
        JsonRepository.update(DB_FILE, "orderId", self.__orderId, self.to_dict())

    def cancelOrder(self): 
        self.__status = "cancelled"
        JsonRepository.update(DB_FILE, "orderId", self.__orderId, self.to_dict())
        
        items = self.loadOrderItems()
        for item in items:
            item.releaseQuota()

    def getByUser(self, user_id): #READ
        all_data = JsonRepository.find_all(DB_FILE)
        results = []
        for d in all_data:
            if d.get("userId") == user_id:
                results.append(Order.from_dict(d))
        return results

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
        from models.user import User
        from models.concert import Concert
        
        user_data = JsonRepository.find_by_id("users.json", "userId", data_dict.get("userId", ""))
        user = User.from_dict(user_data) if user_data else None
        
        concert_data = JsonRepository.find_by_id("concerts.json", "concertId", data_dict.get("concertId", ""))
        concert = Concert.from_dict(concert_data) if concert_data else None
        
        order = cls(
            user=user,
            concert=concert,
            totalAmount=data_dict.get("totalAmount", 0.0),
            status=data_dict.get("status", "pending")
        )
        order.validate()
        JsonRepository.insert(DB_FILE, order.to_dict())
        return order 