"""
Abstract base class BaseModel untuk aplikasi ConcertIn.
Menjadi parent class untuk semua model, memaksakan interface konsisten
melalui abstract methods (to_dict, from_dict, validate) dan menyediakan atribut umum.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import uuid


class BaseModel(ABC):
    """
    Abstract base class untuk seluruh model ConcertIn.

    Attributes:
        _id (str): Unique identifier menggunakan uuid4.
        _created_at (datetime): Timestamp pembuatan objek.
    """

    def __init__(self, id=None, created_at=None):
        """
        Inisialisasi BaseModel.

        Args:
            id (str, optional): Unique identifier. Auto-generated jika tidak diberikan.
            created_at (datetime|str, optional): Timestamp pembuatan. Default: sekarang.
        """
        self._id = id or str(uuid.uuid4())
        self._created_at = self._parse_datetime(created_at) or datetime.now()

    @staticmethod
    def _parse_datetime(value):
        """Helper: parse datetime dari string ISO atau kembalikan as-is."""
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    @property
    def id(self):
        """Getter untuk unique identifier."""
        return self._id

    @id.setter
    def id(self, value):
        """Setter untuk unique identifier."""
        self._id = value

    @property
    def created_at(self):
        """Getter untuk timestamp pembuatan."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Setter untuk timestamp pembuatan."""
        self._created_at = self._parse_datetime(value) or self._created_at

    @abstractmethod
    def to_dict(self):
        """Konversi instance ke dictionary untuk serialisasi JSON."""
        pass

    @abstractmethod
    def from_dict(self, data):
        """Buat instance dari dictionary."""
        pass

    @abstractmethod
    def validate(self):
        """Validasi atribut model sesuai business rules."""
        pass

    def __str__(self):
        """Representasi string dari BaseModel."""
        return f"BaseModel(id={self._id}, created_at={self._created_at.isoformat()})"
