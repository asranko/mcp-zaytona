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
    4. مصادر أسباب النزول والتفاسير الإضافية (44 مصدراً إضافياً):
       asbab_nuzul, durr_manthur, nazm_durar, ghareeb_quran, gharaib_quran, tadhkirat_areeb,
       durr_masun, lubab_ulum, manar, safwat, ayat_ahkam, aysar_jazairi, aysar_homod,
       burhan_bahrani, tawilat_najmiyya, tibyan_tusi, tabarani, ibn_arafa, jawahir_thaalbi,
       safi_kashani, sirat_mustaqim, muntakhab, nahr_madd, aaqam, jilani, hubari, ibn_arabi,
       ibn_abi_zamnin, tustari, fairuzabadi, qummi, nasai, hidayah_maki, bayan_saadah,
       sufyan_thawri, sadr_mutaallhin, abd_razzaq, furat_kufi, hawari, mujahid, taysir_atfiyyish,
       taysir_qattan, jawahir_khalili, hashiyat_sawi, haqaiq_sulami, rumuz_kunuz, ruh_bayan,
       araais_bayan, nuzhat_qulub, majma_bayan, mahasin_tawil, mukhtasar_katheer, muqatil,
       himyan_zad
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


def get_deep_ayah_analysis(
    surah: int,
    ayah: int,
    sources: list[str] | None = None,
) -> dict:
    """تحليل معرفي وبحثي موحد لآية قرآنية يجمع التفسير، الكلمات، الإعراب، الصرف، أسباب النزول، والقراءات.

    surah: رقم السورة (1-114).
    ayah: رقم الآية.
    sources: قائمة اختيارية بمصادر التفسير المطلوبة.
    """
    ref = AyahReference(surah=surah, ayah=ayah)
    
    # 1. جلب بيانات السورة الأساسية
    surah_row = query_one(
        "SELECT surahName, makkiMadani FROM surah_stats WHERE surahNo = ?",
        (ref.surah,),
    )
    surah_name = surah_row["surahName"] if surah_row else ""
    revelation_type = surah_row["makkiMadani"] if surah_row else ""

    # 2. جلب نص الآية الكريمة وعدد الكلمات
    ayah_data = get_ayah(ref.surah, ref.ayah)

    # 3. جلب أسباب النزول
    nuzool_data = get_ayah_nuzool(ref.surah, ref.ayah)

    # 4. جلب القراءات المختلفة للآية
    qeraat_rows = query_all(
        "SELECT q.wordNo, q.content, q.note, r.word"
        " FROM qeraat_info q"
        " JOIN word_content_rasm r"
        "   ON r.surahNo=q.surahNo AND r.ayahNo=q.ayahNo AND r.wordNo=q.wordNo"
        " WHERE q.surahNo = ? AND q.ayahNo = ?"
        "   AND q.content LIKE '@%'"
        " ORDER BY q.wordNo",
        (ref.surah, ref.ayah),
    )
    qeraat_entries = []
    for r in qeraat_rows:
        if r["content"].startswith("لا خلاف بين القراء"):
            continue
        entry = {
            "word_no": r["wordNo"],
            "word": r["word"],
            "qeraat_raw": r["content"],
        }
        if r.get("note"):
            entry["note"] = r["note"]
        qeraat_entries.append(entry)

    # 5. جلب التفاسير المطلوبة (افتراضياً: الميسر، السعدي، ابن كثير، القرطبي، في ظلال القرآن)
    active_sources = sources or ["moyassar", "saadi", "katheer", "qurtubi", "fi_zilal"]
    tafsir_data = get_ayah_tafsir(ref.surah, ref.ayah, active_sources)

    # 6. جلب التحليل اللغوي لجميع الكلمات في دفعة واحدة (Bulk Fetch) لضمان الكفاءة القصوى
    words_rows = query_all(
        "SELECT r.wordNo, r.word, r.rasm,"
        "       m.meaning,"
        "       i.irabMushakkal,"
        "       s.sarf,"
        "       ws.root, ws.repeatitionCount"
        " FROM word_content_rasm r"
        " LEFT JOIN word_content_meaning m"
        "   ON m.surahNo=r.surahNo AND m.ayahNo=r.ayahNo AND m.wordNo=r.wordNo"
        " LEFT JOIN word_content_irab i"
        "   ON i.surahNo=r.surahNo AND i.ayahNo=r.ayahNo AND i.wordNo=r.wordNo"
        " LEFT JOIN word_content_sarf s"
        "   ON s.surahNo=r.surahNo AND s.ayahNo=r.ayahNo AND s.wordNo=r.wordNo"
        " LEFT JOIN word_statistics ws"
        "   ON ws.surahNo=r.surahNo AND ws.ayahNo=r.ayahNo AND ws.wordNo=r.wordNo"
        " WHERE r.surahNo = ? AND r.ayahNo = ?"
        " ORDER BY r.wordNo",
        (ref.surah, ref.ayah),
    )
    
    words_analysis = []
    for row in words_rows:
        rasm_note = row["rasm"] if row["rasm"] and row["rasm"] != "-" else None
        w_data = {
            "word_no": row["wordNo"],
            "word": row["word"],
            "meaning": row["meaning"],
            "irab": row["irabMushakkal"],
            "sarf": row["sarf"],
            "root": row["root"],
            "frequency": row["repeatitionCount"],
        }
        if rasm_note:
            w_data["rasm_note"] = rasm_note
        words_analysis.append(w_data)

    # 7. صياغة الهيكل المعرفي الفريد للـ Cognitive Insights وإرشادات العرض
    saadi_text = ""
    katheer_text = ""
    for entry in tafsir_data.get("tafsirs", []):
        if entry["source"] == "saadi":
            saadi_text = entry["text"]
        elif entry["source"] == "katheer":
            katheer_text = entry["text"]
            
    cognitive_insights = {
        "principle": f"الآية الكريمة: {{{ayah_data.get('text')}}} [سورة {ref.surah} آية {ref.ayah}]",
        "application": f"تفسير السعدي: {saadi_text[:400]}..." if saadi_text else "الرجاء مراجعة التفاسير المرفقة لاستخلاص التطبيق.",
        "effect": f"تفسير ابن كثير: {katheer_text[:400]}..." if katheer_text else "الرجاء مراجعة التفاسير المرفقة لاستخلاص الأثر.",
        "_display_instructions": (
            "أنت الآن ريكي الشريك المعرفي. استنبط من هذه الآية وتفاسيرها وتحليل كلماتها "
            "كبسولة الزيتونة المعرفية الثلاثية: المبدأ الجوهري العام، التطبيق العملي الواقعي، "
            "والأثر الروحي والعملي المتوقع."
        )
    }

    return {
        "surah": ref.surah,
        "ayah": ref.ayah,
        "surah_name": surah_name,
        "revelation_type": revelation_type,
        "ayah_text": ayah_data.get("text"),
        "word_count": ayah_data.get("word_count"),
        "tafsirs": tafsir_data.get("tafsirs", []),
        "words_analysis": words_analysis,
        "nuzool": nuzool_data,
        "qeraat": qeraat_entries,
        "cognitive_insights": cognitive_insights,
    }


def register(mcp: FastMCP) -> None:
    mcp.tool(name="fetch_ayah", annotations=_ANNOTATIONS)(get_ayah)
    mcp.tool(name="fetch_tafsir", annotations=_ANNOTATIONS)(get_ayah_tafsir)
    mcp.tool(name="fetch_nuzool_reason", annotations=_ANNOTATIONS)(get_ayah_nuzool)
    mcp.tool(name="deep_ayah_analysis", annotations=_ANNOTATIONS)(get_deep_ayah_analysis)

