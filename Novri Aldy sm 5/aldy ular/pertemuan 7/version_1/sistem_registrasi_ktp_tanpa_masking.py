#!/usr/bin/env python3
"""Sistem registrasi data KTP berbasis console menggunakan SQLite.

Catatan privasi:
- Gunakan data fiktif untuk latihan.
- Database SQLite ini tidak dienkripsi; jangan gunakan untuk menyimpan data KTP
  nyata tanpa pengamanan, otorisasi, dan persetujuan yang sesuai.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import sqlite3


DB_PATH = Path(__file__).resolve().with_name("data_ktp.db")

JENIS_KELAMIN = ("Laki-laki", "Perempuan")
AGAMA = (
    "Islam",
    "Kristen",
    "Katolik",
    "Hindu",
    "Buddha",
    "Konghucu",
    "Kepercayaan lainnya",
)
STATUS_PERKAWINAN = ("Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati")


@dataclass
class KTPRecord:
    """Model data untuk satu catatan KTP."""

    nik: str
    nama: str
    tempat_lahir: str
    tanggal_lahir: str  # Format ISO: YYYY-MM-DD
    alamat: str
    jenis_kelamin: str
    agama: str
    status_perkawinan: str
    pekerjaan: str

    def __post_init__(self) -> None:
        """Bersihkan spasi dan validasi data agar model selalu konsisten."""
        for field_name in (
            "nik",
            "nama",
            "tempat_lahir",
            "tanggal_lahir",
            "alamat",
            "jenis_kelamin",
            "agama",
            "status_perkawinan",
            "pekerjaan",
        ):
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, value.strip())

        if not re.fullmatch(r"[0-9]{16}", self.nik):
            raise ValueError("NIK harus terdiri dari tepat 16 digit angka.")

        required_fields = {
            "nama": self.nama,
            "tempat lahir": self.tempat_lahir,
            "tanggal lahir": self.tanggal_lahir,
            "alamat": self.alamat,
            "jenis kelamin": self.jenis_kelamin,
            "agama": self.agama,
            "status perkawinan": self.status_perkawinan,
            "pekerjaan": self.pekerjaan,
        }
        empty_fields = [label for label, value in required_fields.items() if not value]
        if empty_fields:
            raise ValueError("Kolom wajib tidak boleh kosong: " + ", ".join(empty_fields))

        try:
            parsed_date = date.fromisoformat(self.tanggal_lahir)
        except ValueError as exc:
            raise ValueError("Tanggal lahir harus valid dengan format YYYY-MM-DD.") from exc
        if parsed_date.isoformat() != self.tanggal_lahir:
            raise ValueError("Tanggal lahir harus menggunakan format YYYY-MM-DD.")
        if parsed_date > date.today():
            raise ValueError("Tanggal lahir tidak boleh berada di masa depan.")

        if self.jenis_kelamin not in JENIS_KELAMIN:
            raise ValueError("Pilihan jenis kelamin tidak valid.")
        if self.agama not in AGAMA:
            raise ValueError("Pilihan agama tidak valid.")
        if self.status_perkawinan not in STATUS_PERKAWINAN:
            raise ValueError("Pilihan status perkawinan tidak valid.")


class KTPManager:
    """Mengelola penyimpanan, daftar, dan pencarian data KTP di SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        """Buat tabel jika belum tersedia."""
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ktp (
                    nik TEXT PRIMARY KEY
                        CHECK(length(nik) = 16 AND nik NOT GLOB '*[^0-9]*'),
                    nama TEXT NOT NULL CHECK(trim(nama) <> ''),
                    tempat_lahir TEXT NOT NULL CHECK(trim(tempat_lahir) <> ''),
                    tanggal_lahir TEXT NOT NULL,
                    alamat TEXT NOT NULL CHECK(trim(alamat) <> ''),
                    jenis_kelamin TEXT NOT NULL,
                    agama TEXT NOT NULL,
                    status_perkawinan TEXT NOT NULL,
                    pekerjaan TEXT NOT NULL CHECK(trim(pekerjaan) <> '')
                )
                """
            )

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> KTPRecord:
        return KTPRecord(
            nik=row["nik"],
            nama=row["nama"],
            tempat_lahir=row["tempat_lahir"],
            tanggal_lahir=row["tanggal_lahir"],
            alamat=row["alamat"],
            jenis_kelamin=row["jenis_kelamin"],
            agama=row["agama"],
            status_perkawinan=row["status_perkawinan"],
            pekerjaan=row["pekerjaan"],
        )

    def add_record(self, record: KTPRecord) -> None:
        """Simpan catatan baru. NIK yang sama akan ditolak oleh database."""
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO ktp (
                    nik, nama, tempat_lahir, tanggal_lahir, alamat,
                    jenis_kelamin, agama, status_perkawinan, pekerjaan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.nik,
                    record.nama,
                    record.tempat_lahir,
                    record.tanggal_lahir,
                    record.alamat,
                    record.jenis_kelamin,
                    record.agama,
                    record.status_perkawinan,
                    record.pekerjaan,
                ),
            )

    def get_all_records(self) -> list[KTPRecord]:
        """Ambil semua catatan, diurutkan berdasarkan nama."""
        rows = self.connection.execute(
            "SELECT * FROM ktp ORDER BY nama COLLATE NOCASE"
        ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def search_records(self, query: str) -> list[KTPRecord]:
        """Cari berdasarkan NIK lengkap atau bagian dari nama."""
        query = query.strip()
        rows = self.connection.execute(
            """
            SELECT * FROM ktp
            WHERE nik = ? OR nama LIKE ? COLLATE NOCASE
            ORDER BY nama COLLATE NOCASE
            """,
            (query, f"%{query}%"),
        ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def get_by_nik(self, nik: str) -> KTPRecord | None:
        """Ambil satu profil berdasarkan NIK lengkap."""
        row = self.connection.execute(
            "SELECT * FROM ktp WHERE nik = ?", (nik.strip(),)
        ).fetchone()
        return self._row_to_record(row) if row else None

    def close(self) -> None:
        self.connection.close()


def prompt_required(label: str) -> str:
    """Minta teks yang wajib diisi, ulangi jika kosong."""
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print(f"{label} wajib diisi. Silakan coba lagi.")


def prompt_nik() -> str:
    while True:
        nik = input("NIK (16 digit): ").strip()
        if re.fullmatch(r"[0-9]{16}", nik):
            return nik
        print("NIK tidak valid. Masukkan tepat 16 digit angka tanpa spasi atau tanda baca.")


def prompt_date_of_birth() -> str:
    while True:
        value = input("Tanggal lahir (YYYY-MM-DD, contoh 2005-08-17): ").strip()
        try:
            parsed = date.fromisoformat(value)
            if parsed.isoformat() != value:
                raise ValueError
            if parsed > date.today():
                print("Tanggal lahir tidak boleh di masa depan.")
                continue
            return value
        except ValueError:
            print("Tanggal tidak valid. Gunakan format YYYY-MM-DD, misalnya 2005-08-17.")


def prompt_choice(label: str, choices: tuple[str, ...]) -> str:
    """Tampilkan pilihan bernomor dan kembalikan pilihan yang valid."""
    print(f"\n{label}:")
    for index, choice in enumerate(choices, start=1):
        print(f"  {index}. {choice}")

    while True:
        selected = input(f"Pilih nomor (1-{len(choices)}): ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(choices):
            return choices[int(selected) - 1]
        print("Pilihan tidak valid. Masukkan nomor dari daftar di atas.")


def add_ktp(manager: KTPManager) -> None:
    print("\n=== Tambah Data KTP ===")
    nik = prompt_nik()
    nama = prompt_required("Nama lengkap")
    tempat_lahir = prompt_required("Tempat lahir")
    tanggal_lahir = prompt_date_of_birth()
    alamat = prompt_required("Alamat lengkap")
    jenis_kelamin = prompt_choice("Jenis kelamin", JENIS_KELAMIN)
    agama = prompt_choice("Agama", AGAMA)
    status_perkawinan = prompt_choice("Status perkawinan", STATUS_PERKAWINAN)
    pekerjaan = prompt_required("Pekerjaan")

    try:
        record = KTPRecord(
            nik=nik,
            nama=nama,
            tempat_lahir=tempat_lahir,
            tanggal_lahir=tanggal_lahir,
            alamat=alamat,
            jenis_kelamin=jenis_kelamin,
            agama=agama,
            status_perkawinan=status_perkawinan,
            pekerjaan=pekerjaan,
        )
        manager.add_record(record)
        print("Data KTP berhasil disimpan.")
    except ValueError as error:
        print(f"Data tidak valid: {error}")
    except sqlite3.IntegrityError:
        print("Gagal menyimpan: NIK tersebut sudah terdaftar.")
    except sqlite3.Error as error:
        print(f"Terjadi masalah database: {error}")


def show_record_list(records: list[KTPRecord]) -> None:
    """Tampilkan ringkasan data dengan NIK lengkap."""
    if not records:
        print("Belum ada data yang cocok.")
        return

    print(f"\nDitemukan {len(records)} data:")
    print("No.  Nama                         NIK                 Tanggal lahir  Jenis kelamin")
    print("-" * 86)
    for index, record in enumerate(records, start=1):
        name = record.nama[:27]
        print(
            f"{index:<4} {name:<28} {record.nik:<19} "
            f"{record.tanggal_lahir:<14} {record.jenis_kelamin}"
        )


def show_all_ktp(manager: KTPManager) -> None:
    print("\n=== Semua Data Terdaftar ===")
    try:
        show_record_list(manager.get_all_records())
    except sqlite3.Error as error:
        print(f"Gagal membaca database: {error}")


def search_ktp(manager: KTPManager) -> None:
    print("\n=== Cari Data KTP ===")
    query = prompt_required("Masukkan NIK lengkap atau nama (boleh sebagian)")
    try:
        show_record_list(manager.search_records(query))
    except sqlite3.Error as error:
        print(f"Gagal mencari data: {error}")


def show_ktp_detail(manager: KTPManager) -> None:
    """Tampilkan profil lengkap menggunakan NIK lengkap sebagai pencarian."""
    print("\n=== Detail Profil KTP ===")
    nik = prompt_nik()
    try:
        record = manager.get_by_nik(nik)
        if record is None:
            print("Data dengan NIK tersebut tidak ditemukan.")
            return

        
        # Data profil yang akan ditampilkan
        fields = [
            ("NIK", record.nik),
            ("Nama lengkap", record.nama),
            ("Tempat lahir", record.tempat_lahir),
            ("Tanggal lahir", record.tanggal_lahir),
            ("Alamat", record.alamat),
            ("Jenis kelamin", record.jenis_kelamin),
            ("Agama", record.agama),
            ("Status perkawinan", record.status_perkawinan),
            ("Pekerjaan", record.pekerjaan),
        ]

        # Menghitung lebar kotak secara otomatis
        label_width = max(len(label) for label, _ in fields)
        content_width = max(
            len(f"{label:<{label_width}} : {value}")
            for label, value in fields
        )

        border = "+" + "-" * (content_width + 2) + "+"

        # Menampilkan kotak profil
        print("\n" + border)
        print("| " + "DETAIL PROFIL PEMILIK KTP".center(content_width) + " |")
        print(border)

        for label, value in fields:
            line = f"{label:<{label_width}} : {value}"
            print("| " + line.ljust(content_width) + " |")

        print(border)

    except sqlite3.Error as error:
        print(f"Gagal membaca detail data: {error}")


def show_menu() -> None:
    print("\n========== SISTEM REGISTRASI KTP ==========")
    print("1. Tambah data KTP")
    print("2. Tampilkan semua data")
    print("3. Cari data berdasarkan nama atau NIK")
    print("4. Tampilkan detail profil berdasarkan NIK")
    print("0. Keluar")
    print("===========================================")


def main() -> None:
    try:
        manager = KTPManager()
    except sqlite3.Error as error:
        print(f"Database tidak dapat dibuka: {error}")
        return

    print("Sistem Registrasi KTP (versi latihan)")
    print(f"Lokasi database: {DB_PATH}")
    try:
        while True:
            show_menu()
            choice = input("Pilih menu: ").strip()

            if choice == "1":
                add_ktp(manager)
            elif choice == "2":
                show_all_ktp(manager)
            elif choice == "3":
                search_ktp(manager)
            elif choice == "4":
                show_ktp_detail(manager)
            elif choice == "0":
                print("Program selesai. Data tetap tersimpan di database.")
                break
            else:
                print("Menu tidak valid. Pilih 1, 2, 3, 4, atau 0.")
    except (KeyboardInterrupt, EOFError):
        print("\nProgram dihentikan. Data yang sudah disimpan tetap ada.")
    finally:
        manager.close()


if __name__ == "__main__":
    main()
