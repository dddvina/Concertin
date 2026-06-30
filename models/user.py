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
    Model User (Base Class).
    """

    def __init__(self, userId=None, name="", email="", password="", role="cust", created_at=None):
        super().__init__(id=userId, created_at=created_at)
        self.__userId = self.id
        self.__name = name
        self.__email = email
        self.__password = password
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
        self.__password = value

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, value):
        self.__role = value

    # ── Instance Methods ────────────────────────────────────

    def register(self):
        self.validate()
        all_users = JsonRepository.find_all(DB_FILE)
        for u in all_users:
            if u.get("email") == self.__email:
                raise DuplicateEmailException()
        JsonRepository.insert(DB_FILE, self.to_dict())

    def login(self, email, pw):
        return self.__email == email and self.__password == pw

    def logout(self):
        pass

    def validate(self):
        Validator.validate_not_empty(self.__name, "name")
        Validator.validate_email(self.__email)
        Validator.validate_enum(self.__role, ["admin", "cust"], "role")

    def to_dict(self):
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
        role = data.get("role", "cust")
        if role == "admin":
            return Admin(
                userId=data.get("userId"),
                name=data.get("name", ""),
                email=data.get("email", ""),
                password=data.get("password", ""),
                created_at=data.get("created_at")
            )
        else:
            return Customer(
                userId=data.get("userId"),
                name=data.get("name", ""),
                email=data.get("email", ""),
                password=data.get("password", ""),
                created_at=data.get("created_at")
            )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.__userId}, name={self.__name}, email={self.__email})"

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_all():
        return len(JsonRepository.find_all(DB_FILE))

    @staticmethod
    def get_by_role(role):
        all_data = JsonRepository.find_all(DB_FILE)
        return [User.from_dict(d) for d in all_data if d.get("role", "cust") == role]

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        role = data_dict.get("role", "cust")
        if role == "admin":
            user = Admin(
                name=data_dict.get("name", ""),
                email=data_dict.get("email", ""),
                password=data_dict.get("password", "")
            )
        else:
            user = Customer(
                name=data_dict.get("name", ""),
                email=data_dict.get("email", ""),
                password=data_dict.get("password", "")
            )
        user.register()
        return user


class Admin(User):
    """Subclass User untuk Admin."""
    def __init__(self, userId=None, name="", email="", password="", created_at=None):
        super().__init__(userId, name, email, password, "admin", created_at)

    def manage_system(self):
        pass


class Customer(User):
    """Subclass User untuk Customer biasa."""
    def __init__(self, userId=None, name="", email="", password="", created_at=None):
        super().__init__(userId, name, email, password, "cust", created_at)

    def view_history(self):
        pass