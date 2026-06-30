"""
Model Concert untuk aplikasi ConcertIn."""

from datetime import datetime
from models.base_model import BaseModel
from repositories.json_repository import JsonRepository
from utils.validator import Validator

DB_FILE = "concerts.json"


class Concert(BaseModel):


    def __init__(self, concertId=None, title="", artistLineup=None,
                 venueName="", venueAddress="", dateTime=None,
                 genre="", status="upcoming", created_at=None):
        super().__init__(id=concertId, created_at=created_at)
        self.__concertId = self.id
        self.__title = title
        self.__artistLineup = artistLineup if artistLineup else []
        self.__venueName = venueName
        self.__venueAddress = venueAddress
        if dateTime is None:
            self.__dateTime = datetime.now()
        elif isinstance(dateTime, str):
            self.__dateTime = datetime.fromisoformat(dateTime)
        else:
            self.__dateTime = dateTime
        self.__genre = genre
        self.__status = status

    # ── Properties ──────────────────────────────────────────

    @property
    def concertId(self):
        return self.__concertId

    @concertId.setter
    def concertId(self, value):
        self.__concertId = value

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value

    @property
    def artistLineup(self):
        return self.__artistLineup

    @artistLineup.setter
    def artistLineup(self, value):
        self.__artistLineup = value

    @property
    def venueName(self):
        return self.__venueName

    @venueName.setter
    def venueName(self, value):
        self.__venueName = value

    @property
    def venueAddress(self):
        return self.__venueAddress

    @venueAddress.setter
    def venueAddress(self, value):
        self.__venueAddress = value

    @property
    def dateTime(self):
        return self.__dateTime

    @dateTime.setter
    def dateTime(self, value):
        if isinstance(value, str):
            self.__dateTime = datetime.fromisoformat(value)
        else:
            self.__dateTime = value

    @property
    def genre(self):
        return self.__genre

    @genre.setter
    def genre(self, value):
        self.__genre = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    # ── Instance Methods ────────────────────────────────────

    def validate(self):
        """Validasi atribut konser."""
        Validator.validate_not_empty(self.__title, "title")
        Validator.validate_not_empty(self.__venueName, "venueName")
        Validator.validate_not_empty(self.__venueAddress, "venueAddress")
        Validator.validate_not_empty(self.__genre, "genre")
        Validator.validate_enum(self.__status,
                                ["upcoming", "ongoing", "completed", "cancelled"], "status")

    def to_dict(self):
        """Konversi Concert ke dictionary."""
        return {
            "concertId": self.__concertId,
            "title": self.__title,
            "artistLineup": self.__artistLineup,
            "venueName": self.__venueName,
            "venueAddress": self.__venueAddress,
            "dateTime": self.__dateTime.isoformat(),
            "genre": self.__genre,
            "status": self.__status,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        """Buat instance Concert dari dictionary."""
        return Concert(
            concertId=data.get("concertId"),
            title=data.get("title", ""),
            artistLineup=data.get("artistLineup", []),
            venueName=data.get("venueName", ""),
            venueAddress=data.get("venueAddress", ""),
            dateTime=data.get("dateTime"),
            genre=data.get("genre", ""),
            status=data.get("status", "upcoming"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        artists = ", ".join(self.__artistLineup)
        return (f"Concert(id={self.__concertId}, title={self.__title}, "
                f"artists=[{artists}], venue={self.__venueName}, "
                f"date={self.__dateTime.strftime('%Y-%m-%d %H:%M')}, "
                f"genre={self.__genre}, status={self.__status})")

    def getAll(self):
        """Ambil semua konser dari database."""
        all_data = JsonRepository.find_all(DB_FILE)
        return [Concert.from_dict(d) for d in all_data]

    def search(self, keyword):
        """Cari konser berdasarkan keyword (judul, genre, venue, artis)."""
        keyword_lower = keyword.lower()
        all_concerts = self.getAll()
        results = []
        for c in all_concerts:
            if (keyword_lower in c.title.lower() or
                    keyword_lower in c.genre.lower() or
                    keyword_lower in c.venueName.lower() or
                    any(keyword_lower in a.lower() for a in c.artistLineup)):
                results.append(c)
        return results

    def getById(self, concert_id):
        data = JsonRepository.find_by_id(DB_FILE, "concertId", concert_id)
        if data:
            return Concert.from_dict(data)
        return None

    # ── Static Methods ──────────────────────────────────────

    @staticmethod
    def count_by_status(status):
        """Hitung jumlah konser dengan status tertentu."""
        all_data = JsonRepository.find_all(DB_FILE)
        return sum(1 for d in all_data if d.get("status") == status)

    # ── Class Methods ───────────────────────────────────────

    @classmethod
    def create(cls, data_dict):
        """Factory method: buat dan simpan Concert baru."""
        concert = cls(
            title=data_dict.get("title", ""),
            artistLineup=data_dict.get("artistLineup", []),
            venueName=data_dict.get("venueName", ""),
            venueAddress=data_dict.get("venueAddress", ""),
            dateTime=data_dict.get("dateTime"),
            genre=data_dict.get("genre", ""),
            status=data_dict.get("status", "upcoming")
        )
        concert.validate()
        JsonRepository.insert(DB_FILE, concert.to_dict())
        return concert
