"""Adapter for classical Arabic lexicons stored in lexicons.db."""

import sqlite3
from pathlib import Path

from tafsir.db import QuranDataError
from tafsir.data_loader import get_lexicon_db_path


class LexiconAdapter:
    """Reads classical Arabic lexicons definitions from lexicons.db."""

    def _get_conn(self) -> sqlite3.Connection | None:
        db_path = get_lexicon_db_path()
        if not db_path.exists():
            return None
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        return conn

    def get_definitions(self, root: str) -> dict[str, str | None]:
        """Fetch definitions for a given root from multiple lexicons."""
        conn = self._get_conn()
        if conn is None:
            return {}

        results = {}
        lexicons = {
            "lisanularab": "lisanularab",
            "maqayeesul_luga": "maqayeesul_luga",
            "mufradat_alfajul_quran": "mufradat_alfajul_quran",
        }

        try:
            for key, table in lexicons.items():
                row = conn.execute(
                    f"SELECT meanings FROM {table} WHERE word = ?", (root,)
                ).fetchone()
                results[key] = row["meanings"] if row else None
            return results
        except sqlite3.DatabaseError as exc:
            raise QuranDataError(f"خطأ في الاستعلام عن المعاجم للجذر {root}: {exc}") from exc
        finally:
            conn.close()

    def search_roots(self, query: str, limit: int = 50) -> list[str]:
        """Search for roots starting with or containing a query."""
        conn = self._get_conn()
        if conn is None:
            return []
        try:
            rows = conn.execute(
                "SELECT DISTINCT word FROM maqayeesul_luga WHERE word LIKE ? LIMIT ?",
                (f"{query}%", limit),
            ).fetchall()
            return [r["word"] for r in rows]
        except sqlite3.DatabaseError as exc:
            raise QuranDataError(f"خطأ في البحث عن الجذور: {exc}") from exc
        finally:
            conn.close()
