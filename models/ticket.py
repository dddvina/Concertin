"""
Model Ticket untuk aplikasi ConcertIn.
Merepresentasikan kategori tiket untuk sebuah konser beserta manajemen kuota.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from typing import TYPE_CHECKING, Optional
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator
from utils.exceptions import TicketNotAvailableException, InsufficientQuotaException

if TYPE_CHECKING:
    from models.concert import Concert

DB_FILE = "tickets.json"


class Ticket(BaseModel):


    def __init__(self, ticketId: Optional[str] = None, concert: Optional['Concert'] = None, category: str = "REG",
                 price: float = 0.0, totalQuota: int = 0, remainingQuota: Optional[int] = None, created_at=None):
        super().__init__(id=ticketId, created_at=created_at)
        self.__ticketId = self.id
        self.__concert = concert # Komposisi dari Concert
        self.__category = category
        self.__price = float(price)
        self.__totalQuota = int(totalQuota)
        self.__remainingQuota = int(remainingQuota) if remainingQuota is not None else int(totalQuota)

    # ── Properties ──────────────────────────────────────────

    @property
    def ticketId(self):
        return self.__ticketId

    @ticketId.setter
    def ticketId(self, value):
        self.__ticketId = value

    @property
    def concert(self):
        return self.__concert

    @concert.setter
    def concert(self, value):
        self.__concert = value

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value):
        self.__category = value

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        self.__price = float(value)

    @property
    def totalQuota(self):
        return self.__totalQuota

    @totalQuota.setter
    def totalQuota(self, value):
        self.__totalQuota = int(value)

    @property
    def remainingQuota(self):
        return self.__remainingQuota

    @remainingQuota.setter
    def remainingQuota(self, value):
        self.__remainingQuota = int(value)

    # ── Instance Methods ────────────────────────────────────

    def validate(self):
        """Validasi atribut tiket."""
        if not self.__concert:
            raise ValueError("Validasi gagal: Ticket harus memiliki objek Concert.")
        Validator.validate_enum(self.__category, ["VIP", "REG"], "category")
        Validator.validate_positive_number(self.__price, "price")
        Validator.validate_positive_number(self.__totalQuota, "totalQuota")

    def to_dict(self):
        """Konversi Ticket ke dictionary."""
        return {
            "ticketId": self.__ticketId,
            "concertId": self.__concert.concertId if self.__concert else "",
            "category": self.__category,
            "price": self.__price,
            "totalQuota": self.__totalQuota,
            "remainingQuota": self.__remainingQuota,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        from models.concert import Concert
        
        # Load concert dynamically
        concert_data = JsonRepository.find_by_id("concerts.json", "concertId", data.get("concertId"))
        concert = Concert.from_dict(concert_data) if concert_data else None

        """Buat instance Ticket dari dictionary."""
        return Ticket(
            ticketId=data.get("ticketId"),
            concert=concert,
            category=data.get("category", "REG"),
            price=data.get("price", 0.0),
            totalQuota=data.get("totalQuota", 0),
            remainingQuota=data.get("remainingQuota"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        c_id = self.__concert.concertId if self.__concert else "Unknown"
        return (f"Ticket(id={self.__ticketId}, concert={c_id}, "
                f"category={self.__category}, price=Rp{self.__price:,.0f}, "
                f"remaining={self.__remainingQuota}/{self.__totalQuota})")

    def checkAvailability(self):
        """Cek apakah tiket masih tersedia."""
        return self.__remainingQuota > 0

    def reserveTicket(self, qty):
        """
        Pesan tiket dengan mengurangi remaining quota.

        Args:
            qty (int): Jumlah tiket yang dipesan.

        Returns:
            bool: True jika pemesanan berhasil.
        """
        if not self.checkAvailability():
            raise TicketNotAvailableException()
        if qty > self.__remainingQuota:
            raise InsufficientQuotaException(
                f"Kuota tersisa hanya {self.__remainingQuota}, tidak dapat memesan {qty} tiket."
            )
        self.__remainingQuota -= qty
        JsonRepository.update(DB_FILE, "ticketId", self.__ticketId, self.to_dict())
        return True

    def getByConcert(self, concert_obj):
        all_data = JsonRepository.find_all(DB_FILE)
        results = []
        for d in all_data:
            if d.get("concertId") == concert_obj.concertId:
                t = Ticket.from_dict(d)
                t.concert = concert_obj
                results.append(t)
        return results

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_available():
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(1 for d in all_data if d.get("remainingQuota", 0) > 0)

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        """Factory method: buat dan simpan Ticket baru."""
        from models.concert import Concert
        concert_data = JsonRepository.find_by_id("concerts.json", "concertId", data_dict.get("concertId"))
        concert = Concert.from_dict(concert_data) if concert_data else None

        ticket = cls(
            concert=concert,
            category=data_dict.get("category", "REG"),
            price=data_dict.get("price", 0.0),
            totalQuota=data_dict.get("totalQuota", 0),
            remainingQuota=data_dict.get("remainingQuota")
        )
        ticket.validate()
        JsonRepository.insert(DB_FILE, ticket.to_dict())
        return ticket
