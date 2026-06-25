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
        __id (str): Unique identifier menggunakan uuid4.
        __created_at (datetime): Timestamp pembuatan objek.
    """

    def __init__(self, id=None, created_at=None):
        """
        Inisialisasi BaseModel.

        Args:
            id (str, optional): Unique identifier. Auto-generated jika tidak diberikan.
            created_at (datetime|str, optional): Timestamp pembuatan. Default: sekarang.
        """
        self.__id = id if id else str(uuid.uuid4())
        if created_at is None:
            self.__created_at = datetime.now()
        elif isinstance(created_at, str):
            self.__created_at = datetime.fromisoformat(created_at)
        else:
            self.__created_at = created_at

    @property
    def id(self):
        """Getter untuk unique identifier."""
        return self.__id

    @id.setter
    def id(self, value):
        """Setter untuk unique identifier."""
        self.__id = value

    @property
    def created_at(self):
        """Getter untuk timestamp pembuatan."""
        return self.__created_at

    @created_at.setter
    def created_at(self, value):
        """Setter untuk timestamp pembuatan."""
        if isinstance(value, str):
            self.__created_at = datetime.fromisoformat(value)
        else:
            self.__created_at = value

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
        return f"BaseModel(id={self.__id}, created_at={self.__created_at.isoformat()})"
