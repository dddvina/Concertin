"""
Service Concert untuk aplikasi ConcertIn.
"""

from models.concert import Concert
from services.user_service import UserService
from utils.exceptions import ConcertInException


class ConcertService:
    """Layer service untuk entitas Concert."""

    @staticmethod
    def create_concert(data_dict, requester_id):  #Create
        try:
            UserService.require_admin(requester_id)
            return Concert.create(data_dict)
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal membuat konser: {e}")

    @staticmethod
    def get_all_concerts(): #read
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
    def delete_concert(concert_id, requester_id): #Delete
        """Hapus konser beserta tiket terkait (admin only)."""
        try:
            UserService.require_admin(requester_id)
            existing = Concert().getById(concert_id)
            if not existing:
                raise ConcertInException("Konser tidak ditemukan.")
            from repositories.json_repository import JsonRepository
            all_tickets = JsonRepository.find_all("tickets.json")
            filtered = [t for t in all_tickets if t.get("concertId") != concert_id]
            JsonRepository.save("tickets.json", filtered)
            JsonRepository.delete("concerts.json", "concertId", concert_id)
            return existing
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal menghapus konser: {e}")

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