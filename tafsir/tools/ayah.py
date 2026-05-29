"""Ayah-level MCP tools: get_ayah, get_ayah_tafsir, get_ayah_nuzool."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from tafsir.adapters import ADAPTERS
from tafsir.db import query_all, query_one
from tafsir.models import (
    TAFSIR_ATTRIBUTIONS,
    AyahReference,
    AyahResponse,
    TafsirEntry,
    TafsirResponse,
    TafsirSource,
)
from tafsir.normalize import reconstruct_ayah

_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def get_ayah(
    surah: int,
    ayah: int,
    include: list[str] | None = None,
) -> dict:
    """جلب نص آية قرآنية بالرسم العثماني.

    include: حقول اختيارية — قائمة تحتوي أي من: 'tajweed', 'irab'
    """
    ref = AyahReference(surah=surah, ayah=ayah)
    include = include or []

    rasm_rows = query_all(
        "SELECT word, wordNo FROM word_content_rasm"
        " WHERE surahNo = ? AND ayahNo = ? ORDER BY wordNo",
        (ref.surah, ref.ayah),
    )
    text = reconstruct_ayah(rasm_rows)

    tajweed = None
    if "tajweed" in include:
        row = query_one(
            "SELECT tajweed FROM ayah_content_tajweed WHERE surahNo = ? AND ayahNo = ?",
            (ref.surah, ref.ayah),
        )
        tajweed = row["tajweed"] if row else None

    irab = None
    if "irab" in include:
        row = query_one(
            "SELECT irabAyah1 FROM ayah_content_irab WHERE surahNo = ? AND ayahNo = ?",
            (ref.surah, ref.ayah),
        )
        irab = row["irabAyah1"] if row else None

    return AyahResponse(
        surah=ref.surah,
        ayah=ref.ayah,
        text=text,
        tajweed=tajweed,
        irab=irab,
        word_count=len(rasm_rows),
    ).model_dump()


def get_ayah_tafsir(
    surah: int,
    ayah: int,
    sources: list[str] | None = None,
) -> dict:
    """جلب تفسير آية من مصدر أو أكثر.

    sources: قائمة المصادر المطلوبة (default: ['saadi']).
    القيم المتاحة:
    1. الأساسية:
       tabary, katheer, baghawy, saadi, moyassar, mukhtasar_ar, mukhtasar_en, mukhtasar_bn
    2. الجلالين:
       jalalayn
    3. الموسعة (33 تفسيراً إضافياً):
       tahrir_wa_tanwir, qurtubi, kashshaf, mafatih_al_ghayb, mizan, ruh_al_maani, fath_al_qadir,
       adwa_al_bayan, sharawi, wasit, bayani, fi_zilal, qushayri, ibn_ajiba, nasafi, abu_al_saud,
       baydawi, khazin, ibn_juzayy, thalabi, mawirdi, samani, raghib_isfahani, ibn_atiyya,
       zad_al_masir, bahr_al_muhit, samarqandi, ibn_abi_hatim, wahidi_wasit, wahidi_wajiz,
       izz_bin_abd_salam, ibn_rajab, maturidi
    """
    ref = AyahReference(surah=surah, ayah=ayah)
    requested = [TafsirSource(s) for s in (sources or ["saadi"])]

    tafsirs: list[TafsirEntry] = []
    for src in requested:
        adapter = ADAPTERS.get(src)
        if not adapter:
            continue
        text = adapter.fetch(ref.surah, ref.ayah)
        if text:
            tafsirs.append(
                TafsirEntry(
                    source=src,
                    attribution=TAFSIR_ATTRIBUTIONS[src],
                    text=text,
                )
            )

    return TafsirResponse(
        surah=ref.surah,
        ayah=ref.ayah,
        tafsirs=tafsirs,
    ).model_dump()


def get_ayah_nuzool(surah: int, ayah: int) -> dict:
    """سبب نزول الآية إن ثبت في المصادر المعتمدة.

    201 آية فقط لها أسباب نزول موثقة في القاعدة.
    النص يُعاد كما هو بإسناده الكامل — لا تلخيص.
    """
    ref = AyahReference(surah=surah, ayah=ayah)
    row = query_one(
        "SELECT nozoolInfo FROM ayah_content_nozool WHERE surahNo = ? AND ayahNo = ?",
        (ref.surah, ref.ayah),
    )
    if not row or not row["nozoolInfo"]:
        return {
            "surah": ref.surah,
            "ayah": ref.ayah,
            "available": False,
            "reason": "لم يثبت سبب نزول لهذه الآية في المصادر المعتمدة",
        }
    return {
        "surah": ref.surah,
        "ayah": ref.ayah,
        "available": True,
        "text": row["nozoolInfo"],
    }


def register(mcp: FastMCP) -> None:
    mcp.tool(name="fetch_ayah", annotations=_ANNOTATIONS)(get_ayah)
    mcp.tool(name="fetch_tafsir", annotations=_ANNOTATIONS)(get_ayah_tafsir)
    mcp.tool(name="fetch_nuzool_reason", annotations=_ANNOTATIONS)(get_ayah_nuzool)
