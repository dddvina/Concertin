"""
Modul Validator untuk aplikasi ConcertIn.
Berisi static method untuk validasi input menggunakan regex dan business rules.
"""

import re
from datetime import datetime
from utils.exceptions import ValidationException


class Validator:
    """Utility class berisi static method validasi data input."""

    @staticmethod
    def validate_email(email):
        """Validasi format email menggunakan regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationException("Format email tidak valid.", "email")
        return True

    @staticmethod
    def validate_password(password):
        """Validasi password: minimal 8 karakter, ada huruf dan angka."""
        if len(password) < 8:
            raise ValidationException("Password minimal 8 karakter.", "password")
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationException("Password harus mengandung huruf.", "password")
        if not re.search(r'[0-9]', password):
            raise ValidationException("Password harus mengandung angka.", "password")
        return True

    @staticmethod
    def validate_not_empty(value, field_name):
        """Validasi bahwa value tidak kosong atau None."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValidationException(f"{field_name} tidak boleh kosong.", field_name)
        return True

    @staticmethod
    def validate_positive_number(value, field_name):
        """Validasi bahwa value adalah angka positif."""
        try:
            num = float(value)
            if num <= 0:
                raise ValidationException(f"{field_name} harus berupa angka positif.", field_name)
        except (TypeError, ValueError):
            raise ValidationException(f"{field_name} harus berupa angka.", field_name)
        return True

    @staticmethod
    def validate_date_future(date):
        """Validasi bahwa tanggal di masa depan."""
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except ValueError:
                raise ValidationException("Format tanggal tidak valid.", "date")
        if date <= datetime.now():
            raise ValidationException("Tanggal harus di masa depan.", "date")
        return True

    @staticmethod
    def validate_enum(value, allowed_values, field_name):
        """Validasi bahwa value termasuk dalam daftar nilai yang diizinkan."""
        if value not in allowed_values:
            allowed = ', '.join(str(v) for v in allowed_values)
            raise ValidationException(
                f"{field_name} harus salah satu dari: {allowed}.", field_name
            )
        return True
