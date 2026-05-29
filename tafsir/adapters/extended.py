"""Adapter for the 12 extended tafsirs stored in extended_tafsir.db."""

import sqlite3
from pathlib import Path

from tafsir.adapters.base import TafsirAdapter
from tafsir.db import QuranDataError
from tafsir.data_loader import get_extended_db_path



def _escape_like(text: str) -> str:
    return text.replace("!", "!!").replace("%", "!%").replace("_", "!_")


class ExtendedTafsirAdapter(TafsirAdapter):
    """Reads tafsir content from the unified extended_tafsir.db.

    Schema: tafsir_content(source TEXT, surah INT, ayah INT, text TEXT)
    """

    def __init__(self, source: str):
        self.source = source

    def _get_conn(self) -> sqlite3.Connection | None:
        db_path = get_extended_db_path()
        if not db_path.exists():
            return None
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        return conn

    def fetch(self, surah: int, ayah: int) -> str | None:
        conn = self._get_conn()
        if conn is None:
            return None
        try:
            row = conn.execute(
                "SELECT text FROM tafsir_content WHERE source = ? AND surah = ? AND ayah = ?",
                (self.source, surah, ayah),
            ).fetchone()
            return row["text"] if row else None
        except sqlite3.DatabaseError as exc:
            raise QuranDataError(f"خطأ في الاستعلام عن {self.source}: {exc}") from exc
        finally:
            conn.close()

    def search(self, query: str, surah_filter: list[int] | None = None, limit: int = 20) -> list[dict]:
        conn = self._get_conn()
        if conn is None:
            return []
        escaped = _escape_like(query.strip())
        like_param = f"%{escaped}%"
        try:
            if surah_filter:
                placeholders = ",".join("?" * len(surah_filter))
                sql = (
                    f"SELECT surah, ayah, text FROM tafsir_content"
                    f" WHERE source = ? AND text LIKE ? ESCAPE '!'"
                    f" AND surah IN ({placeholders}) LIMIT ?"
                )
                params = (self.source, like_param, *surah_filter, limit)
            else:
                sql = (
                    "SELECT surah, ayah, text FROM tafsir_content"
                    " WHERE source = ? AND text LIKE ? ESCAPE '!' LIMIT ?"
                )
                params = (self.source, like_param, limit)
            rows = conn.execute(sql, params).fetchall()
            return [{"surah": r["surah"], "ayah": r["ayah"], "text": r["text"]} for r in rows]
        except sqlite3.DatabaseError as exc:
            raise QuranDataError(f"خطأ في البحث في {self.source}: {exc}") from exc
        finally:
            conn.close()
