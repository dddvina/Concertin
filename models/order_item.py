"""
Model OrderItem untuk aplikasi ConcertIn.
Merepresentasikan item pesanan yang menghubungkan Order dengan Ticket.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator

DB_FILE = "order_items.json"


class OrderItem(BaseModel):
    """
    Model OrderItem merepresentasikan satu baris pesanan tiket.

    Attributes:
        __itemId (str): Unique item identifier.
        __orderId (str): ID order terkait (FK).
        __ticketId (str): ID tiket terkait (FK).
        __quantity (int): Jumlah tiket yang dipesan.
        __subTotal (float): Total harga untuk item ini (qty * price).
    """

    def __init__(self, itemId=None, orderId="", ticketId="",
                 quantity=0, subTotal=0.0, created_at=None):
        super().__init__(id=itemId, created_at=created_at)
        self.__itemId = self.id
        self.__orderId = orderId
        self.__ticketId = ticketId
        self.__quantity = int(quantity)
        self.__subTotal = float(subTotal)

    # ── Properties ──────────────────────────────────────────

    @property
    def itemId(self):
        return self.__itemId

    @itemId.setter
    def itemId(self, value):
        self.__itemId = value

    @property
    def orderId(self):
        return self.__orderId

    @orderId.setter
    def orderId(self, value):
        self.__orderId = value

    @property
    def ticketId(self):
        return self.__ticketId

    @ticketId.setter
    def ticketId(self, value):
        self.__ticketId = value

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        self.__quantity = int(value)

    @property
    def subTotal(self):
        return self.__subTotal

    @subTotal.setter
    def subTotal(self, value):
        self.__subTotal = float(value)

    # ── Instance Methods ────────────────────────────────────

    def validate(self):
        """Validasi atribut order item."""
        Validator.validate_not_empty(self.__orderId, "orderId")
        Validator.validate_not_empty(self.__ticketId, "ticketId")
        Validator.validate_positive_number(self.__quantity, "quantity")

    def to_dict(self):
        return {
            "itemId": self.__itemId,
            "orderId": self.__orderId,
            "ticketId": self.__ticketId,
            "quantity": self.__quantity,
            "subTotal": self.__subTotal,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return OrderItem(
            itemId=data.get("itemId"),
            orderId=data.get("orderId", ""),
            ticketId=data.get("ticketId", ""),
            quantity=data.get("quantity", 0),
            subTotal=data.get("subTotal", 0.0),
            created_at=data.get("created_at")
        )

    def __str__(self):
        return (f"OrderItem(id={self.__itemId}, order={self.__orderId}, "
                f"ticket={self.__ticketId}, qty={self.__quantity}, "
                f"subtotal=Rp{self.__subTotal:,.0f})")

    def calcSubtotal(self):
        """
        Polymorphism: Menghitung subtotal.
        Mencari harga tiket di DB dan mengalikan dengan quantity.
        """
        ticket_data = JsonRepository.find_by_id("tickets.json", "ticketId", self.__ticketId)
        if ticket_data:
            price = float(ticket_data.get("price", 0))
            self.__subTotal = self.__quantity * price
        return self.__subTotal

    def updateQty(self, qty):
        """Update quantity dan hitung ulang subtotal."""
        self.__quantity = int(qty)
        self.calcSubtotal()
        JsonRepository.update(DB_FILE, "itemId", self.__itemId, self.to_dict())

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def get_by_order(order_id):
        """Ambil semua order item milik sebuah order."""
        all_data = JsonRepository.find_all(DB_FILE)
        return [OrderItem.from_dict(d) for d in all_data if d.get("orderId") == order_id]

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        item = cls(
            orderId=data_dict.get("orderId", ""),
            ticketId=data_dict.get("ticketId", ""),
            quantity=data_dict.get("quantity", 0),
            subTotal=data_dict.get("subTotal", 0.0)
        )
        item.validate()
        item.calcSubtotal()
        JsonRepository.insert(DB_FILE, item.to_dict())
        return item
