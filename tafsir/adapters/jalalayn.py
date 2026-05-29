import sqlite3
from typing import Any
from tafsir.adapters.base import TafsirAdapter
from tafsir.db import get_connection, QuranDataError
from tafsir.data_loader import get_jalalayn_db_path

def _escape_like(text: str) -> str:
    return text.replace("!", "!!").replace("%", "!%").replace("_", "!_")

class JalalaynAdapter(TafsirAdapter):
    def fetch(self, surah: int, ayah: int) -> str | None:
        db_path = get_jalalayn_db_path()
        if not db_path.exists():
            return None
        
        conn = get_connection(db_path)
        try:
            row = conn.execute(
                "SELECT text FROM tafsir_entries WHERE surah = ? AND ayah = ? AND source_id = 'jalalayn'",
                (surah, ayah)
            ).fetchone()
            return row["text"] if row else None
        except sqlite3.DatabaseError as exc:
            raise QuranDataError(f"خطأ في الاستعلام عن تفسير الجلالين: {exc}") from exc
        finally:
            conn.close()

    def search(self, query: str, surah_filter: list[int] | None = None, limit: int = 20) -> list[dict]:
        db_path = get_jalalayn_db_path()
        if not db_path.exists():
            return []

        escaped = _escape_like(query.strip())
        like_param = f"%{escaped}%"

        conn = get_connection(db_path)
        try:
            if surah_filter:
                placeholders = ",".join("?" * len(surah_filter))
                sql = (
                    f"SELECT surah, ayah, text FROM tafsir_entries"
                    f" WHERE source_id = 'jalalayn' AND text LIKE ? ESCAPE '!'"
                    f" AND surah IN ({placeholders}) LIMIT ?"
                )
                params = (like_param, *surah_filter, limit)
            else:
                sql = (
                    "SELECT surah, ayah, text FROM tafsir_entries"
                    " WHERE source_id = 'jalalayn' AND text LIKE ? ESCAPE '!' LIMIT ?"
                )
                params = (like_param, limit)

            rows = conn.execute(sql, params).fetchall()
            return [
                {
                    "surah": r["surah"],
                    "ayah": r["ayah"],
                    "text": r["text"],
                }
                for r in rows
            ]
        except sqlite3.DatabaseError as exc:
            raise QuranDataError(f"خطأ في البحث في تفسير الجلالين: {exc}") from exc
        finally:
            conn.close()
