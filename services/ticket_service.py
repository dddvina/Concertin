"""
Service Ticket untuk aplikasi ConcertIn.
"""

from models.ticket import Ticket
from repositories.json_repository import JsonRepository
from utils.exceptions import ConcertInException


class TicketService:
    """Layer service untuk entitas Ticket."""

    @staticmethod
    def create_ticket(data_dict):
        try:
            return Ticket.create(data_dict)
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal membuat tiket: {e}")

    @staticmethod
    def get_tickets_by_concert(concert_id):
        try:
            return Ticket().getByConcert(concert_id)
        except Exception as e:
            raise ConcertInException(f"Gagal mengambil tiket: {e}")

    @staticmethod
    def reserve_ticket(ticket_id, qty):
        try:
            data = JsonRepository.find_by_id(
                "tickets.json", "ticketId", ticket_id
            )
            if not data:
                raise ConcertInException("Tiket tidak ditemukan.")
            ticket = Ticket.from_dict(data)
            ticket.reserveTicket(qty)
            return ticket
        except ConcertInException:
            raise
        except Exception as e:
            raise ConcertInException(f"Gagal memesan tiket: {e}")

    @staticmethod
    def get_statistics():
        """Hitung total tiket terjual (total - remaining)."""
        all_data = JsonRepository.find_all("tickets.json")
        sold = sum(
            int(d.get("totalQuota", 0)) - int(d.get("remainingQuota", 0))
            for d in all_data
        )
        return {"tickets_sold": sold}

    @staticmethod
    def get_ticket_by_id(ticket_id):
        data = JsonRepository.find_by_id(
            "tickets.json", "ticketId", ticket_id
        )
        if not data:
            raise ConcertInException("Tiket tidak ditemukan.")
        return Ticket.from_dict(data)
