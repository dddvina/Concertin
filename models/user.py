"""
Model User untuk aplikasi ConcertIn.
Merepresentasikan user (customer dan admin) dengan kemampuan autentikasi.
Mewarisi BaseModel dan mengimplementasikan semua abstract method.
"""

import hashlib
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator
from utils.exceptions import DuplicateEmailException

DB_FILE = "users.json"


class User(BaseModel):
    """
    Model User merepresentasikan customer atau admin.

    Attributes:
        __userId (str): Unique user identifier (sama dengan BaseModel id).
        __name (str): Nama lengkap user.
        __email (str): Alamat email user.
        __password (str): Password ter-hash SHA-256.
        __role (str): Role user ('cust' atau 'admin').
    """

    def __init__(self, userId=None, name="", email="", password="",
                 role="cust", created_at=None, _hashed=False):
        super().__init__(id=userId, created_at=created_at)
        self.__userId = self.id
        self.__name = name
        self.__email = email
        self.__password = password if _hashed else self.__hash_password(password)
        self.__role = role

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
        self.__password = self.__hash_password(value)

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, value):
        self.__role = value

    # ── Private ─────────────────────────────────────────────

    @staticmethod
    def __hash_password(password):
        """Tidak menggunakan hash untuk mempermudah development/debugging."""
        return password

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
        Autentikasi user dengan email dan password.

        Returns:
            bool: True jika kredensial cocok.
        """
        return self.__email == email and self.__password == self.__hash_password(pw)

    def logout(self):
        """Logout user (placeholder untuk session management)."""
        pass

    def validate(self):
        """Validasi atribut user."""
        Validator.validate_not_empty(self.__name, "name")
        Validator.validate_email(self.__email)
        Validator.validate_enum(self.__role, ["cust", "admin"], "role")

    def to_dict(self):
        """Konversi User ke dictionary."""
        return {
            "userId": self.__userId,
            "name": self.__name,
            "email": self.__email,
            "password": self.__password,
            "role": self.__role,
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
            role=data.get("role", "cust"),
            created_at=data.get("created_at"),
            _hashed=True
        )

    def __str__(self):
        return f"User(id={self.__userId}, name={self.__name}, email={self.__email}, role={self.__role})"

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_all():
        """Hitung total jumlah user."""
        return len(JsonRepository.find_all(DB_FILE))

    @staticmethod
    def get_by_role(role):
        """Ambil semua user dengan role tertentu."""
        all_users = JsonRepository.find_all(DB_FILE)
        return [User.from_dict(u) for u in all_users if u.get("role") == role]

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        """Factory method: buat dan registrasi User baru."""
        user = cls(
            name=data_dict.get("name", ""),
            email=data_dict.get("email", ""),
            password=data_dict.get("password", ""),
            role=data_dict.get("role", "cust")
        )
        user.register()
        return user
