"""
Model OrderItem untuk aplikasi ConcertIn.
Merepresentasikan item pesanan yang menghubungkan Order dengan Ticket.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from typing import TYPE_CHECKING, Optional
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator

if TYPE_CHECKING:
    from models.order import Order
    from models.ticket import Ticket

DB_FILE = "order_items.json"


class OrderItem(BaseModel):

    def __init__(self, itemId: Optional[str] = None, order: Optional['Order'] = None, 
                 ticket: Optional['Ticket'] = None, quantity: int = 0, subTotal: float = 0.0, created_at=None):
        super().__init__(id=itemId, created_at=created_at)
        self.__itemId = self.id
        self.__order = order     # Agregasi ke Order
        self.__ticket = ticket   # Agregasi ke Ticket
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
    def order(self):
        return self.__order

    @order.setter
    def order(self, value):
        self.__order = value

    @property
    def ticket(self):
        return self.__ticket

    @ticket.setter
    def ticket(self, value):
        self.__ticket = value

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
        if not self.__order:
            raise ValueError("Validasi gagal: OrderItem harus memiliki objek Order.")
        if not self.__ticket:
            raise ValueError("Validasi gagal: OrderItem harus memiliki objek Ticket.")
        Validator.validate_positive_number(self.__quantity, "quantity")

    def to_dict(self):
        return {
            "itemId": self.__itemId,
            "orderId": self.__order.orderId if self.__order else "",
            "ticketId": self.__ticket.ticketId if self.__ticket else "",
            "quantity": self.__quantity,
            "subTotal": self.__subTotal,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        from models.ticket import Ticket
        
        ticket_data = JsonRepository.find_by_id("tickets.json", "ticketId", data.get("ticketId"))
        ticket = Ticket.from_dict(ticket_data) if ticket_data else None
        
        # Order object is typically injected by the Order when loading its items,
        # or loaded dynamically to prevent infinite recursion if needed.
        return OrderItem(
            itemId=data.get("itemId"),
            order=None, # To be set by caller or Order
            ticket=ticket,
            quantity=data.get("quantity", 0),
            subTotal=data.get("subTotal", 0.0),
            created_at=data.get("created_at")
        )

    def __str__(self):
        o_id = self.__order.orderId if self.__order else "Unknown"
        t_id = self.__ticket.ticketId if self.__ticket else "Unknown"
        return (f"OrderItem(id={self.__itemId}, order={o_id}, "
                f"ticket={t_id}, qty={self.__quantity}, "
                f"subtotal=Rp{self.__subTotal:,.0f})")

    def calcSubtotal(self):
        if self.__ticket:
            self.__subTotal = self.__quantity * self.__ticket.price
        return self.__subTotal

    def updateQty(self, qty):
        self.__quantity = int(qty)
        self.calcSubtotal()
        JsonRepository.update(DB_FILE, "itemId", self.__itemId, self.to_dict())

    def releaseQuota(self):
        if self.__ticket:
            self.__ticket.remainingQuota = self.__ticket.remainingQuota + self.__quantity
            JsonRepository.update("tickets.json", "ticketId", self.__ticket.ticketId, self.__ticket.to_dict())

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def get_by_order(order_obj):
        all_data = JsonRepository.find_all(DB_FILE)
        results = []
        for d in all_data:
            if d.get("orderId") == order_obj.orderId:
                item = OrderItem.from_dict(d)
                item.order = order_obj
                results.append(item)
        return results

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        from models.ticket import Ticket
        
        # Assuming order object is passed in data_dict as 'order', or we load ticket only
        ticket_data = JsonRepository.find_by_id("tickets.json", "ticketId", data_dict.get("ticketId", ""))
        ticket = Ticket.from_dict(ticket_data) if ticket_data else None
        
        item = cls(
            order=data_dict.get("order"), # Expecting caller to pass Order object here
            ticket=ticket,
            quantity=data_dict.get("quantity", 0),
            subTotal=data_dict.get("subTotal", 0.0)
        )
        item.validate()
        item.calcSubtotal()
        JsonRepository.insert(DB_FILE, item.to_dict())
        return item