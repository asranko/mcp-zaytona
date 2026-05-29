from typing import Any
from tafsir.adapters.base import TafsirAdapter
from tafsir.db import query_one, query_all, QuranDataError
from tafsir.models import TafsirSource

# Pre-built SQL queries for get_ayah_tafsir
_TAFSIR_SQL = {
    TafsirSource.tabary: (
        "SELECT tafsir FROM tafsir_tabary WHERE sura = ? AND aya = ?",
        "tafsir",
    ),
    TafsirSource.katheer: (
        "SELECT tafsir FROM tafsir_katheer WHERE sura = ? AND aya = ?",
        "tafsir",
    ),
    TafsirSource.baghawy: (
        "SELECT tafsir FROM tafsir_baghawy WHERE sura = ? AND aya = ?",
        "tafsir",
    ),
    TafsirSource.saadi: (
        "SELECT tafsir FROM tafsir_saadi WHERE sura = ? AND aya = ?",
        "tafsir",
    ),
    TafsirSource.moyassar: (
        "SELECT tafsir FROM tafsir_moyassar WHERE sura = ? AND aya = ?",
        "tafsir",
    ),
    TafsirSource.mukhtasar_ar: (
        "SELECT Mukhtasarar FROM QuranTafseer WHERE surahNo = ? AND ayahNo = ?",
        "Mukhtasarar",
    ),
    TafsirSource.mukhtasar_en: (
        "SELECT Mukhtasaren FROM QuranTafseer WHERE surahNo = ? AND ayahNo = ?",
        "Mukhtasaren",
    ),
    TafsirSource.mukhtasar_bn: (
        "SELECT Mukhtasarbn FROM QuranTafseer WHERE surahNo = ? AND ayahNo = ?",
        "Mukhtasarbn",
    ),
}

# Pre-built SQL queries for search_tafsir
_SEARCH_TAFSIR_SQL = {
    TafsirSource.tabary: (
        "SELECT sura AS s, aya AS a, tafsir AS t FROM tafsir_tabary WHERE tafsir LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.katheer: (
        "SELECT sura AS s, aya AS a, tafsir AS t FROM tafsir_katheer WHERE tafsir LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.baghawy: (
        "SELECT sura AS s, aya AS a, tafsir AS t FROM tafsir_baghawy WHERE tafsir LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.saadi: (
        "SELECT sura AS s, aya AS a, tafsir AS t FROM tafsir_saadi WHERE tafsir LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.moyassar: (
        "SELECT sura AS s, aya AS a, tafsir AS t FROM tafsir_moyassar WHERE tafsir LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.mukhtasar_ar: (
        "SELECT surahNo AS s, ayahNo AS a, Mukhtasarar AS t FROM QuranTafseer WHERE Mukhtasarar LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.mukhtasar_en: (
        "SELECT surahNo AS s, ayahNo AS a, Mukhtasaren AS t FROM QuranTafseer WHERE Mukhtasaren LIKE ? ESCAPE '!'",
        "s",
    ),
    TafsirSource.mukhtasar_bn: (
        "SELECT surahNo AS s, ayahNo AS a, Mukhtasarbn AS t FROM QuranTafseer WHERE Mukhtasarbn LIKE ? ESCAPE '!'",
        "s",
    ),
}

def _escape_like(text: str) -> str:
    return text.replace("!", "!!").replace("%", "!%").replace("_", "!_")

class QuranDBAdapter(TafsirAdapter):
    def __init__(self, source: TafsirSource):
        self.source = source

    def fetch(self, surah: int, ayah: int) -> str | None:
        sql, col = _TAFSIR_SQL[self.source]
        row = query_one(sql, (surah, ayah))
        return row[col] if row and row[col] else None

    def search(self, query: str, surah_filter: list[int] | None = None, limit: int = 20) -> list[dict]:
        base_sql, sura_alias = _SEARCH_TAFSIR_SQL[self.source]
        escaped = _escape_like(query.strip())
        like_param = f"%{escaped}%"

        if surah_filter:
            placeholders = ",".join("?" * len(surah_filter))
            sql = f"{base_sql} AND {sura_alias} IN ({placeholders}) LIMIT ?"
            params = (like_param, *surah_filter, limit)
        else:
            sql = f"{base_sql} LIMIT ?"
            params = (like_param, limit)

        try:
            rows = query_all(sql, params)
        except QuranDataError:
            return []

        return [
            {
                "surah": r["s"],
                "ayah": r["a"],
                "text": r["t"],
            }
            for r in rows
        ]
