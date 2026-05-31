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


def search_all_tafsirs(
    query: str,
    sources: list[str] | None = None,
    surah_filter: list[int] | None = None,
    limit_per_source: int = 5,
    total_limit: int = 30,
) -> list[dict]:
    """البحث النصي الموحد في تفاسير متعددة (أو جميع الـ 96 مصدراً) دفعة واحدة مع الفلترة والفرز.

    query: نص البحث (LIKE).
    sources: قائمة بأسماء المصادر للبحث فيها (None تعني البحث في المصادر الأساسية الـ 10 الكبرى).
    surah_filter: قائمة أرقام السور (اختياري).
    limit_per_source: أقصى عدد نتائج لكل مصدر فردي (1-20، افتراضي 5).
    total_limit: أقصى عدد نتائج إجمالي يعاد (افتراضي 30).
    """
    if not query or not query.strip():
        return []

    # إذا كانت المصادر فارغة، نقترح 10 مصادر متنوعة كأعمدة للبحث
    if not sources:
        sources = [
            "tabary", "katheer", "baghawy", "saadi", "moyassar", 
            "jalalayn", "qurtubi", "kashshaf", "tahrir_wa_tanwir", "fi_zilal"
        ]

    from tafsir.adapters.extended import SOURCE_TO_SHARD, _open_shard
    from tafsir.data_loader import get_extended_shard_path, get_db_path, get_jalalayn_db_path
    from tafsir.models import TAFSIR_ATTRIBUTIONS
    import sqlite3
    import os

    results = []
    escaped = query.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_")
    like_param = f"%{escaped}%"

    # تجميع وتصنيف المصادر المطلوبة
    quran_req = [s for s in sources if s in ["tabary", "katheer", "baghawy", "saadi", "moyassar", "mukhtasar_ar", "mukhtasar_en", "mukhtasar_bn"]]
    jalalayn_req = "jalalayn" in sources
    
    extended_req = {}
    for s in sources:
        shard = SOURCE_TO_SHARD.get(s)
        if shard:
            extended_req.setdefault(shard, []).append(s)

    # 1. البحث في quran.db
    if quran_req:
        quran_path = get_db_path()
        if quran_path.exists():
            conn = sqlite3.connect(quran_path)
            conn.row_factory = sqlite3.Row
            try:
                for src_name in quran_req:
                    src_results = []
                    try:
                        src_enum = TafsirSource(src_name)
                    except ValueError:
                        continue
                    
                    if src_name in ["tabary", "katheer", "baghawy", "saadi", "moyassar"]:
                        tbl = f"tafsir_{src_name}"
                        if surah_filter:
                            placeholders = ",".join("?" * len(surah_filter))
                            sql = f"SELECT sura AS surah, aya AS ayah, tafsir AS text FROM {tbl} WHERE tafsir LIKE ? ESCAPE '!' AND sura IN ({placeholders}) LIMIT ?"
                            params = (like_param, *surah_filter, limit_per_source)
                        else:
                            sql = f"SELECT sura AS surah, aya AS ayah, tafsir AS text FROM {tbl} WHERE tafsir LIKE ? ESCAPE '!' LIMIT ?"
                            params = (like_param, limit_per_source)
                        rows = conn.execute(sql, params).fetchall()
                        for r in rows:
                            src_results.append({
                                "surah": r["surah"],
                                "ayah": r["ayah"],
                                "source": src_name,
                                "source_name": TAFSIR_ATTRIBUTIONS.get(src_enum, src_name),
                                "snippet": r["text"][:300] + ("…" if len(r["text"]) > 300 else "")
                            })
                    elif src_name in ["mukhtasar_ar", "mukhtasar_en", "mukhtasar_bn"]:
                        col = "Mukhtasarar" if src_name == "mukhtasar_ar" else ("Mukhtasaren" if src_name == "mukhtasar_en" else "Mukhtasarbn")
                        if surah_filter:
                            placeholders = ",".join("?" * len(surah_filter))
                            sql = f"SELECT surahNo AS surah, ayahNo AS ayah, {col} AS text FROM QuranTafseer WHERE {col} LIKE ? ESCAPE '!' AND surahNo IN ({placeholders}) LIMIT ?"
                            params = (like_param, *surah_filter, limit_per_source)
                        else:
                            sql = f"SELECT surahNo AS surah, ayahNo AS ayah, {col} AS text FROM QuranTafseer WHERE {col} LIKE ? ESCAPE '!' LIMIT ?"
                            params = (like_param, limit_per_source)
                        rows = conn.execute(sql, params).fetchall()
                        for r in rows:
                            src_results.append({
                                "surah": r["surah"],
                                "ayah": r["ayah"],
                                "source": src_name,
                                "source_name": TAFSIR_ATTRIBUTIONS.get(src_enum, src_name),
                                "snippet": r["text"][:300] + ("…" if len(r["text"]) > 300 else "")
                            })
                    results.extend(src_results)
            finally:
                conn.close()

    # 2. البحث في jalalayn.db
    if jalalayn_req:
        jalalayn_path = get_jalalayn_db_path()
        if jalalayn_path.exists():
            conn = sqlite3.connect(jalalayn_path)
            conn.row_factory = sqlite3.Row
            try:
                if surah_filter:
                    placeholders = ",".join("?" * len(surah_filter))
                    sql = (
                        f"SELECT surah, ayah, text FROM tafsir_entries"
                        f" WHERE source_id = 'jalalayn' AND text LIKE ? ESCAPE '!'"
                        f" AND surah IN ({placeholders}) LIMIT ?"
                    )
                    params = (like_param, *surah_filter, limit_per_source)
                else:
                    sql = (
                        "SELECT surah, ayah, text FROM tafsir_entries"
                        " WHERE source_id = 'jalalayn' AND text LIKE ? ESCAPE '!' LIMIT ?"
                    )
                    params = (like_param, limit_per_source)
                rows = conn.execute(sql, params).fetchall()
                for r in rows:
                    results.append({
                        "surah": r["surah"],
                        "ayah": r["ayah"],
                        "source": "jalalayn",
                        "source_name": TAFSIR_ATTRIBUTIONS.get(TafsirSource.jalalayn, "تفسير الجلالين"),
                        "snippet": r["text"][:300] + ("…" if len(r["text"]) > 300 else "")
                    })
            finally:
                conn.close()

    # 3. البحث في ملفات الشظايا الـ Extended
    # تنظيف نص البحث ليكون متوافقاً تماماً مع قواعد FTS5 MATCH
    import re
    cleaned_query = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', query.strip())
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
    
    for shard_file, shard_sources in extended_req.items():
        db_path = get_extended_shard_path(shard_file)
        if not db_path.exists():
            continue
        conn = _open_shard(db_path)
        if conn is None:
            continue
        try:
            # للحد الكلي من الاستعلام، نضرب الحد الأقصى للمصدر بعدد المصادر المطلوبة في هذه الشظية
            shard_limit = limit_per_source * len(shard_sources)
            placeholders_src = ",".join("?" * len(shard_sources))
            
            # إذا نجح تنظيف النص لـ FTS، نستخدم الـ MATCH الفائق السرعة، وإلا نتراجع إلى LIKE البطيء كحماية
            if cleaned_query:
                if surah_filter:
                    placeholders_surah = ",".join("?" * len(surah_filter))
                    sql = (
                        f"SELECT source, surah, ayah, text FROM tafsir_fts"
                        f" WHERE source IN ({placeholders_src}) AND tafsir_fts MATCH ?"
                        f" AND surah IN ({placeholders_surah}) LIMIT ?"
                    )
                    params = (*shard_sources, cleaned_query, *surah_filter, shard_limit)
                else:
                    sql = (
                        f"SELECT source, surah, ayah, text FROM tafsir_fts"
                        f" WHERE source IN ({placeholders_src}) AND tafsir_fts MATCH ? LIMIT ?"
                    )
                    params = (*shard_sources, cleaned_query, shard_limit)
            else:
                # Fallback to LIKE if search query contains no alphanumeric characters
                if surah_filter:
                    placeholders_surah = ",".join("?" * len(surah_filter))
                    sql = (
                        f"SELECT source, surah, ayah, text FROM tafsir_content"
                        f" WHERE source IN ({placeholders_src}) AND text LIKE ? ESCAPE '!'"
                        f" AND surah IN ({placeholders_surah}) LIMIT ?"
                    )
                    params = (*shard_sources, like_param, *surah_filter, shard_limit)
                else:
                    sql = (
                        f"SELECT source, surah, ayah, text FROM tafsir_content"
                        f" WHERE source IN ({placeholders_src}) AND text LIKE ? ESCAPE '!' LIMIT ?"
                    )
                    params = (*shard_sources, like_param, shard_limit)
                
            rows = conn.execute(sql, params).fetchall()
            
            # فلترة إضافية للتأكد من ألا يتجاوز أي مفسر حد الـ limit_per_source
            source_counts = {}
            for r in rows:
                src = r["source"]
                source_counts[src] = source_counts.get(src, 0) + 1
                if source_counts[src] <= limit_per_source:
                    try:
                        src_enum = TafsirSource(src)
                        display_name = TAFSIR_ATTRIBUTIONS.get(src_enum, src)
                    except ValueError:
                        display_name = src
                        
                    results.append({
                        "surah": r["surah"],
                        "ayah": r["ayah"],
                        "source": src,
                        "source_name": display_name,
                        "snippet": r["text"][:300] + ("…" if len(r["text"]) > 300 else "")
                    })
        except Exception as e:
            # Fallback to LIKE if FTS fails for any reason (e.g. database schema mismatch)
            try:
                # Retry with LIKE query as fallback
                if surah_filter:
                    placeholders_surah = ",".join("?" * len(surah_filter))
                    sql = (
                        f"SELECT source, surah, ayah, text FROM tafsir_content"
                        f" WHERE source IN ({placeholders_src}) AND text LIKE ? ESCAPE '!'"
                        f" AND surah IN ({placeholders_surah}) LIMIT ?"
                    )
                    params = (*shard_sources, like_param, *surah_filter, shard_limit)
                else:
                    sql = (
                        f"SELECT source, surah, ayah, text FROM tafsir_content"
                        f" WHERE source IN ({placeholders_src}) AND text LIKE ? ESCAPE '!' LIMIT ?"
                    )
                    params = (*shard_sources, like_param, shard_limit)
                rows = conn.execute(sql, params).fetchall()
                source_counts = {}
                for r in rows:
                    src = r["source"]
                    source_counts[src] = source_counts.get(src, 0) + 1
                    if source_counts[src] <= limit_per_source:
                        try:
                            src_enum = TafsirSource(src)
                            display_name = TAFSIR_ATTRIBUTIONS.get(src_enum, src)
                        except ValueError:
                            display_name = src
                            
                        results.append({
                            "surah": r["surah"],
                            "ayah": r["ayah"],
                            "source": src,
                            "source_name": display_name,
                            "snippet": r["text"][:300] + ("…" if len(r["text"]) > 300 else "")
                        })
            except Exception as inner_e:
                print(f"Error querying shard {shard_file}: {inner_e}")
        finally:
            conn.close()

    # ترتيب النتائج حسب السورة والآية، وتطبيق الحد الإجمالي
    results.sort(key=lambda x: (x["surah"], x["ayah"]))
    return results[:total_limit]


def register(mcp: FastMCP) -> None:
    mcp.tool(name="search_quran_text", annotations=_ANNOTATIONS)(search_quran_text)
    mcp.tool(name="search_in_tafsir", annotations=_ANNOTATIONS)(search_tafsir)
    mcp.tool(name="search_all_tafsirs", annotations=_ANNOTATIONS)(search_all_tafsirs)

