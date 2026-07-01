# Modul JSON Repository untuk aplikasi ConcertIn.Semua operasi file dibungkus try-except untuk error handling.


import json
import os


class JsonRepository:


    __base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database"
    )

    @classmethod
    def __get_filepath(cls, filename):
        """Mendapatkan full path untuk sebuah filename."""
        return os.path.join(cls.__base_path, filename)

    @classmethod
    def load(cls, filename):
        """
        Memuat semua record dari file JSON.
        Returns:
            list: Daftar record (dict). Mengembalikan list kosong jika error.
        """
        try:
            filepath = cls.__get_filepath(filename)
            if not os.path.exists(filepath):
                return []
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERROR] Gagal memuat file {filename}: {e}")
            return []

    @classmethod
    def save(cls, filename, data):
        """
        Menyimpan list record ke file JSON.
            data (list): Daftar record yang akan disimpan.
        """
        try:
            filepath = cls.__get_filepath(filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            print(f"[ERROR] Gagal menyimpan file {filename}: {e}")

    @classmethod
    def find_by_id(cls, filename, id_field, id_value):
        """
        Mencari satu record berdasarkan ID.

        Returns:
            dict | None: Record yang cocok, atau None jika tidak ditemukan.
        """
        try:
            data = cls.load(filename)
            for record in data:
                if record.get(id_field) == id_value:
                    return record
            return None
        except Exception as e:
            print(f"[ERROR] Gagal mencari data di {filename}: {e}")
            return None

    @classmethod
    def find_all(cls, filename):
        """read"""
        try:
            return cls.load(filename)
        except Exception as e:
            print(f"[ERROR] Gagal mengambil data dari {filename}: {e}")
            return []

    @classmethod
    def insert(cls, filename, record):
        """create"""
        try:
            data = cls.load(filename)
            data.append(record)
            cls.save(filename, data)
        except Exception as e:
            print(f"[ERROR] Gagal menyisipkan data ke {filename}: {e}")

    @classmethod
    def update(cls, filename, id_field, id_value, updated_record):
        """update."""
        try:
            data = cls.load(filename)
            for i, record in enumerate(data):
                if record.get(id_field) == id_value:
                    data[i] = updated_record
                    break
            cls.save(filename, data)
        except Exception as e:
            print(f"[ERROR] Gagal memperbarui data di {filename}: {e}")

    @classmethod
    def delete(cls, filename, id_field, id_value):
        """delete"""
        try:
            data = cls.load(filename)
            data = [r for r in data if r.get(id_field) != id_value]
            cls.save(filename, data)
        except Exception as e:
            print(f"[ERROR] Gagal menghapus data dari {filename}: {e}")
