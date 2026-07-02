"""
Modul custom exception untuk aplikasi ConcertIn.
Semua exception mewarisi dari base ConcertInException.
"""


class ConcertInException(Exception):

    def __init__(self, message="Terjadi kesalahan pada sistem ConcertIn."):
        self.__message = message
        super().__init__(self.__message)

    @property
    def message(self):
        return self.__message


class UserNotFoundException(ConcertInException):
    """Exception ketika user tidak ditemukan."""

    def __init__(self, message="User tidak ditemukan."):
        super().__init__(message)


class InvalidCredentialsException(ConcertInException):
    """Exception ketika kredensial login tidak valid."""

    def __init__(self, message="Email atau password salah."):
        super().__init__(message)


class TicketNotAvailableException(ConcertInException):
    """Exception ketika tiket tidak tersedia."""

    def __init__(self, message="Tiket tidak tersedia."):
        super().__init__(message)


class InsufficientQuotaException(ConcertInException):
    """Exception ketika kuota tiket tidak mencukupi."""

    def __init__(self, message="Kuota tiket tidak mencukupi."):
        super().__init__(message)


class OrderNotFoundException(ConcertInException):
    """Exception ketika order tidak ditemukan."""

    def __init__(self, message="Order tidak ditemukan."):
        super().__init__(message)


class PaymentFailedException(ConcertInException):
    """Exception ketika proses pembayaran gagal."""

    def __init__(self, message="Pembayaran gagal."):
        super().__init__(message)


class ValidationException(ConcertInException):
    """Exception ketika validasi input gagal."""

    def __init__(self, message="Validasi gagal.", field=None):
        self.__field = field
        full_message = f"Validasi gagal pada field '{field}': {message}" if field else message
        super().__init__(full_message)

    @property
    def field(self):
        return self.__field


class DuplicateEmailException(ConcertInException):
    """Exception ketika email sudah terdaftar."""

    def __init__(self, message="Email sudah terdaftar."):
        super().__init__(message)
