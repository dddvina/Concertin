"""
Service Concert untuk aplikasi ConcertIn.
"""

from models.concert import Concert
from utils.exceptions import ConcertInException


class ConcertService:
    """Layer service untuk entitas Concert."""

    @staticmethod
    def create_concert(data_dict):
        try:
            return Concert.create(data_dict)
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal membuat konser: {e}")

    @staticmethod
    def get_all_concerts():
        try:
            return Concert().getAll()
        except Exception as e:
            raise ConcertInException(f"Gagal mengambil data konser: {e}")

    @staticmethod
    def search_concerts(keyword):
        try:
            return Concert().search(keyword)
        except Exception as e:
            raise ConcertInException(f"Gagal mencari konser: {e}")

    @staticmethod
    def get_concert_by_id(concert_id):
        try:
            result = Concert().getById(concert_id)
            if not result:
                raise ConcertInException("Konser tidak ditemukan.")
            return result
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal mengambil konser: {e}")
