"""
Service User untuk aplikasi ConcertIn.
Menyembunyikan kompleksitas autentikasi dari main.py.
"""

from models.user import User
from repositories.json_repository import JsonRepository
from utils.exceptions import (
    UserNotFoundException, InvalidCredentialsException,
    DuplicateEmailException, ConcertInException
)


class UserService:
    """Layer service untuk entitas User."""

    @staticmethod
    def register(name, email, password, role="cust"):
        try:
            return User.create({
                "name": name,
                "email": email,
                "password": password,
                "role": role
            })
        except (DuplicateEmailException, ConcertInException):
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal registrasi: {e}")

    @staticmethod
    def login(email, password):
        try:
            all_users = JsonRepository.find_all("users.json")
            for u_data in all_users:
                user = User.from_dict(u_data)
                if user.login(email, password):
                    return user
            raise InvalidCredentialsException()
        except InvalidCredentialsException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal login: {e}")

    @staticmethod
    def get_all_users():
        all_data = JsonRepository.find_all("users.json")
        return [User.from_dict(d) for d in all_data]

    @staticmethod
    def get_user_by_id(user_id):
        data = JsonRepository.find_by_id("users.json", "userId", user_id)
        if not data:
            raise UserNotFoundException()
        return User.from_dict(data)

    @staticmethod
    def get_statistics():
        return {
            "total_users": User.count_all(),
            "total_customers": len(User.get_by_role("cust")),
            "total_admins": len(User.get_by_role("admin"))
        }
