"""Full-text and tafsir search MCP tools."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from tafsir.adapters import ADAPTERS
from tafsir.db import QuranDataError, get_connection, query_all
from tafsir.models import TAFSIR_ATTRIBUTIONS, TafsirSource
from tafsir.normalize import normalize_arabic

_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def search_quran_text(
    query: str,
    surah_filter: list[int] | None = None,
    limit: Annotated[int, Field(ge=1, le=100)] = 20,
) -> list[dict]:
    """بحث نصي في آيات القرآن باستخدام FTS5 (يدعم البحث بدون تشكيل).

    query: نص البحث — يُطبَّع تلقائياً (تُزال التشكيلات، تُوحَّد الألفات).
    surah_filter: قائمة أرقام سور لتضييق البحث (اختياري).
    limit: أقصى عدد نتائج (1-100، افتراضي 20).
    يُرجع: [{surah, ayah, text, snippet, score}]
    """
    if not query or not query.strip():
        return []

    normalized = normalize_arabic(query.strip())
    if not normalized:
        return []

    conn = get_connection()
    try:
        if surah_filter:
            # Dynamic IN clause — only ? placeholders, not values
            placeholders = ",".join("?" * len(surah_filter))
            sql = (
                f"SELECT surahNo, ayahNo, text_original,"
                f" snippet(ayah_fts,2,'<m>','</m>','…',15) AS snip,"
                f" rank AS score"
                f" FROM ayah_fts"
                f" WHERE text_normalized MATCH ?"
                f" AND surahNo IN ({placeholders})"
                f" ORDER BY rank LIMIT ?"
            )
            params = (normalized, *surah_filter, limit)
        else:
            sql = (
                "SELECT surahNo, ayahNo, text_original,"
                " snippet(ayah_fts,2,'<m>','</m>','…',15) AS snip,"
                " rank AS score"
                " FROM ayah_fts"
                " WHERE text_normalized MATCH ?"
                " ORDER BY rank LIMIT ?"
            )
            params = (normalized, limit)

        try:
            rows = conn.execute(sql, params).fetchall()
        except Exception:
            return []

        return [
            {
                "surah": r["surahNo"],
                "ayah": r["ayahNo"],
                "text": r["text_original"],
                "snippet": r["snip"],
                "score": r["score"],
            }
            for r in rows
        ]
    finally:
        conn.close()


def search_tafsir(
    query: str,
    source: str = "saadi",
    surah_filter: list[int] | None = None,
    limit: Annotated[int, Field(ge=1, le=100)] = 20,
) -> list[dict]:
    """بحث LIKE في تفسير معين.

    query: نص البحث (بحث تضمين — لا يُطبَّع تلقائياً لأن التفاسير تحوي تشكيلاً).
    source: مصدر التفسير (tabary/katheer/baghawy/saadi/moyassar/
                          mukhtasar_ar/mukhtasar_en/mukhtasar_bn/jalalayn).
    surah_filter: قائمة أرقام سور (اختياري).
    limit: أقصى عدد نتائج (افتراضي 20).
    يُرجع: [{surah, ayah, tafsir_excerpt, source_attribution}]
    """
    if not query or not query.strip():
        return []

    try:
        src = TafsirSource(source)
    except ValueError:
        return []

    adapter = ADAPTERS.get(src)
    if not adapter:
        return []

    results = adapter.search(query, surah_filter, limit)
    attribution = TAFSIR_ATTRIBUTIONS[src]
    return [
        {
            "surah": r["surah"],
            "ayah": r["ayah"],
            "tafsir_excerpt": r["text"][:300] + ("…" if len(r["text"]) > 300 else ""),
            "source_attribution": attribution,
        }
        for r in results
    ]


def register(mcp: FastMCP) -> None:
    mcp.tool(name="search_quran_text", annotations=_ANNOTATIONS)(search_quran_text)
    mcp.tool(name="search_in_tafsir", annotations=_ANNOTATIONS)(search_tafsir)
