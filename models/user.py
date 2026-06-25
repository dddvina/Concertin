"""
Model User untuk aplikasi ConcertIn.
Merepresentasikan user dengan kemampuan autentikasi.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator
from utils.exceptions import DuplicateEmailException

DB_FILE = "users.json"


class User(BaseModel):
    """
    Model User merepresentasikan customer aplikasi.

    Attributes:
        __userId (str): Unique user identifier (sama dengan BaseModel id).
        __name (str): Nama lengkap user.
        __email (str): Alamat email user.
        __password (str): Password user (plaintext).
    """

    def __init__(self, userId=None, name="", email="", password="", created_at=None):
        super().__init__(id=userId, created_at=created_at)
        self.__userId = self.id
        self.__name = name
        self.__email = email
        self.__password = password

    # ── Properties ──────────────────────────────────────────

    @property
    def userId(self):
        return self.__userId

    @userId.setter
    def userId(self, value):
        self.__userId = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        self.__password = value

    # ── Instance Methods ────────────────────────────────────

    def register(self):
        """Registrasi user: validasi, cek duplikat email, simpan ke database."""
        self.validate()
        all_users = JsonRepository.find_all(DB_FILE)
        for u in all_users:
            if u.get("email") == self.__email:
                raise DuplicateEmailException()
        JsonRepository.insert(DB_FILE, self.to_dict())

    def login(self, email, pw):
        """
        Autentikasi user dengan email dan password langsung (plaintext).

        Returns:
            bool: True jika kredensial cocok.
        """
        return self.__email == email and self.__password == pw

    def logout(self):
        """Logout user (placeholder untuk session management / membersihkan state)."""
        pass

    def validate(self):
        """Validasi atribut user."""
        Validator.validate_not_empty(self.__name, "name")
        Validator.validate_email(self.__email)

    def to_dict(self):
        """Konversi User ke dictionary."""
        return {
            "userId": self.__userId,
            "name": self.__name,
            "email": self.__email,
            "password": self.__password,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        """Buat instance User dari dictionary."""
        return User(
            userId=data.get("userId"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            created_at=data.get("created_at")
        )

    def __str__(self):
        return f"User(id={self.__userId}, name={self.__name}, email={self.__email})"

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_all():
        """Hitung total jumlah user."""
        return len(JsonRepository.find_all(DB_FILE))

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        """Factory method: buat dan registrasi User baru."""
        user = cls(
            name=data_dict.get("name", ""),
            email=data_dict.get("email", ""),
            password=data_dict.get("password", "")
        )
        user.register()
        return user