"""
Model Ticket untuk aplikasi ConcertIn.
Merepresentasikan kategori tiket untuk sebuah konser beserta manajemen kuota.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator
from utils.exceptions import TicketNotAvailableException, InsufficientQuotaException

DB_FILE = "tickets.json"


class Ticket(BaseModel):
    """
    Model Ticket merepresentasikan tipe tiket untuk sebuah konser.

    Attributes:
        __ticketId (str): Unique ticket identifier.
        __concertId (str): ID konser terkait (FK).
        __category (str): Kategori tiket ('VIP' atau 'REG').
        __price (float): Harga tiket.
        __totalQuota (int): Total kuota awal tiket.
        __remainingQuota (int): Sisa kuota tiket saat ini.
    """

    def __init__(self, ticketId=None, concertId="", category="REG",
                 price=0.0, totalQuota=0, remainingQuota=None, created_at=None):
        super().__init__(id=ticketId, created_at=created_at)
        self.__ticketId = self.id
        self.__concertId = concertId
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
    def concertId(self):
        return self.__concertId

    @concertId.setter
    def concertId(self, value):
        self.__concertId = value

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
        Validator.validate_not_empty(self.__concertId, "concertId")
        Validator.validate_enum(self.__category, ["VIP", "REG"], "category")
        Validator.validate_positive_number(self.__price, "price")
        Validator.validate_positive_number(self.__totalQuota, "totalQuota")

    def to_dict(self):
        """Konversi Ticket ke dictionary."""
        return {
            "ticketId": self.__ticketId,
            "concertId": self.__concertId,
            "category": self.__category,
            "price": self.__price,
            "totalQuota": self.__totalQuota,
            "remainingQuota": self.__remainingQuota,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        """Buat instance Ticket dari dictionary."""
        return Ticket(
            ticketId=data.get("ticketId"),
            concertId=data.get("concertId", ""),
            category=data.get("category", "REG"),
            price=data.get("price", 0.0),
            totalQuota=data.get("totalQuota", 0),
            remainingQuota=data.get("remainingQuota"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        return (f"Ticket(id={self.__ticketId}, concert={self.__concertId}, "
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

    def getByConcert(self, concert_id):
        """Ambil semua tiket untuk konser tertentu."""
        all_data = JsonRepository.find_all(DB_FILE)
        return [Ticket.from_dict(d) for d in all_data if d.get("concertId") == concert_id]

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_available():
        """Hitung jumlah tiket yang masih tersedia kuotanya."""
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(1 for d in all_data if d.get("remainingQuota", 0) > 0)

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        """Factory method: buat dan simpan Ticket baru."""
        ticket = cls(
            concertId=data_dict.get("concertId", ""),
            category=data_dict.get("category", "REG"),
            price=data_dict.get("price", 0.0),
            totalQuota=data_dict.get("totalQuota", 0),
            remainingQuota=data_dict.get("remainingQuota")
        )
        ticket.validate()
        JsonRepository.insert(DB_FILE, ticket.to_dict())
        return ticket
