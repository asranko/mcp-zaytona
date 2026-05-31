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
    sources: list[TafsirSource] | None = None,
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
    requested = sources or [TafsirSource.saadi]

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
    sources: list[TafsirSource] | None = None,
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


SCHOLAR_SCHOOLS: dict[str, dict[str, str]] = {
    "tabary": {
        "theology": "أهل السنة / مجتهد مستقل",
        "fiqh": "جريري (مذهب مستقل)",
        "method": "تفسير بالمأثور ورواية الآثار ومناقشة اللغة والإعراب وترجيح الأقوال"
    },
    "katheer": {
        "theology": "أهل السنة / أثري",
        "fiqh": "شافعي",
        "method": "تفسير بالمأثور (تفسير القرآن بالقرآن ثم السنة ثم الآثار)، ونقد الروايات والأسانيد"
    },
    "baghawy": {
        "theology": "أهل السنة / أثري",
        "fiqh": "شافعي",
        "method": "تفسير بالمأثور، تهذيب تفسير الثعلبي، التركيز على الروايات الصحيحة والسنن"
    },
    "saadi": {
        "theology": "أهل السنة / أثري",
        "fiqh": "حنبلي",
        "method": "تفسير بياني ميسر، التركيز على المقاصد التربوية والأخلاقية والأحكام العملية دون تشقيق لغوي"
    },
    "moyassar": {
        "theology": "أهل السنة",
        "fiqh": "مذهب أهل السنة العام",
        "method": "تفسير وجيز معاصر بعبارة سهلة مبني على أصح الأقوال"
    },
    "jalalayn": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "شافعي",
        "method": "تفسير وجيز ومختصر للغاية باللفظ المرادف وحل المشكل الإعرابي"
    },
    "kashshaf": {
        "theology": "معتزلي",
        "fiqh": "حنفي",
        "method": "بياني بلاغي لغوي فائق، وإثبات الأصول المعتزلية الخمسة من خلال الآيات"
    },
    "qurtubi": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "مالكي",
        "method": "تركيز شديد على آيات الأحكام واستنباط الفقه واللغة، مع نقد الإسرائيليات ورواية الآثار"
    },
    "mafatih_al_ghayb": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "شافعي",
        "method": "تفسير عقلي كلامي موسوعي، مناقشة المعتزلة والفلاسفة، والاستدلال بالعلوم الكونية"
    },
    "tahrir_wa_tanwir": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "مالكي",
        "method": "تحليل بلاغي ونحوي ونقدي فائق، إبراز وجوه الإعجاز والمقاصد الشرعية، والتجديد في التفسير"
    },
    "mizan": {
        "theology": "شيعي إمامي",
        "fiqh": "جعفري",
        "method": "تفسير القرآن بالقرآن (تفسير الآية بأخواتها)، أبعاد فلسفية، وعقائدية وبحث روائي"
    },
    "fi_zilal": {
        "theology": "أهل السنة",
        "fiqh": "حركي فكري",
        "method": "تفسير أدبي حركي واجتماعي، معايشة ظلال النص القرآني، وإبراز مقومات العقيدة الإسلامية المعاصرة"
    },
    "sharawi": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "شافعي",
        "method": "خواطر تفسيرية بأسلوب وعظي بياني سهل يستهدف تقريب معاني القرآن للعامة والخاصة"
    },
    "durr_manthur": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "شافعي",
        "method": "تفسير أثري خالص بالروايات المسندة عن النبي صلى الله عليه وسلم والصحابة والتابعين دون تعليق"
    },
    "nazm_durar": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "شافعي",
        "method": "علم المناسبات، إثبات إعجاز الترتيب والتلاؤم بين الآيات والسور"
    },
    "ibn_atiyya": {
        "theology": "أهل السنة / أشعري",
        "fiqh": "مالكي",
        "method": "تفسير بالمأثور واللغة بعبارة محققة مهذبة ورعاية وجوه الإعراب"
    },
    "maturidi": {
        "theology": "أهل السنة / ماتريدي",
        "fiqh": "حنفي",
        "method": "تفسير عقلي كلامي وتأويلات توافق أصول أهل السنة والجماعة"
    }
}


def _normalize_arabic_simple(text: str) -> str:
    """تبسيط وحذف التشكيل والهمزات لتسهيل مطابقة العبارات المفتاحية."""
    if not text:
        return ""
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    # محاولة استخدام pyarabic لإزالة التشكيل
    try:
        import pyarabic.araby as araby
        text = araby.strip_tashkeel(text)
    except Exception:
        pass
    return text.lower()


def _split_into_sentences(text: str) -> list[str]:
    """تقسيم نص التفسير الطويل إلى جمل منفصلة بالاعتماد على الفواصل وعلامات الترقيم."""
    import re
    # تقسيم النص بناءً على السطور والفواصل العربية والإنجليزية والنقاط
    parts = re.split(r'[\n.،؛!؟]+', text)
    sentences = []
    for p in parts:
        p_clean = p.strip()
        if len(p_clean) > 10:  # تجاهل العبارات القصيرة جداً
            sentences.append(p_clean)
    return sentences


def _classify_sentence(sentence: str) -> list[str]:
    """تصنيف الجملة إلى بعد أو أكثر بناءً على العبارات المفتاحية."""
    norm = _normalize_arabic_simple(sentence)
    dims = []
    
    # قاموس المصطلحات المنهجية الإسلامية للأبعاد السبعة
    keywords = {
        "agreement": ["اجمع", "اجماع", "اتفق", "اتفقوا", "لا خلاف", "قول واحد", "بالاجماع", "مجمع عليه"],
        "fiqh_difference": ["فقه", "حكم", "احكام", "فقهاء", "مذهب", "الشافعي", "مالك", "ابو حنيفه", "احمد", "وجوب", "فرض", "حرام", "يجوز", "حلال", "الجمهور", "مذهبنا", "المالكيه", "الشافعيه", "الحنفيه", "الحنابله"],
        "aqeedah_difference": ["عقيده", "توحيد", "صفات", "تاويل", "اشعريه", "معتزله", "الاشاعره", "المعتزله", "اهل السنه", "الاثريه", "رويه الله", "استواء", "مجسمه", "جهميه", "الكلام", "ايمان", "ماتريديه"],
        "linguistic_difference": ["لغه", "نحو", "اعراب", "بلاغه", "بيان", "مجاز", "حقيقه", "تقدير", "نحوي", "نحاه", "سيبويه", "الفراء", "الزجاج", "المبرد", "كسائي", "لغوي", "مجازي"],
        "qiraat_difference": ["قراءه", "قراءات", "وقرا", "قرا", "القراء", "السبعه", "عاصم", "نافع", "ابن كثير", "حمزه", "الكسائي", "ابو عمرو", "ابن عامر", "شاذ", "متواتر"],
        "historical_difference": ["نزلت", "سبب النزول", "روي", "حدثنا", "اخبرنا", "عن ابن عباس", "مجاهد", "قتاده", "الحسن", "السلف", "سياق", "تاريخ", "قصه"],
        "ishari_difference": ["اشاره", "اشاري", "الصوفيه", "صوفي", "حقيقه", "بطن", "ذوق", "سلوك", "عرفان", "مكاشفه", "تجلي", "السالكين"]
    }
    
    for dim, kws in keywords.items():
        for kw in kws:
            if kw in norm:
                dims.append(dim)
                break
                
    return dims


def compare_tafsir(
    surah: int,
    ayah: int,
    sources: list[TafsirSource] | None = None,
) -> dict:
    """مقارنة تفسير آية بين مفسرين متعددين مع طبقة بنيوية لاستخلاص وتجميع وجوه الاتفاق والاختلاف برمجياً.

    sources: قائمة المصادر المطلوب مقارنتها. الافتراضي: الطبري، ابن كثير، الزمخشري، القرطبي، ابن عاشور، صاحب الميزان.
    """
    ref = AyahReference(surah=surah, ayah=ayah)
    
    # جلب نص الآية
    rasm_rows = query_all(
        "SELECT word, wordNo FROM word_content_rasm"
        " WHERE surahNo = ? AND ayahNo = ? ORDER BY wordNo",
        (ref.surah, ref.ayah),
    )
    ayah_text = reconstruct_ayah(rasm_rows)
    
    # المصادر الافتراضية للمقارنة المتنوعة
    active_sources = sources or [
        TafsirSource.tabary,
        TafsirSource.katheer,
        TafsirSource.kashshaf,
        TafsirSource.qurtubi,
        TafsirSource.tahrir_wa_tanwir,
        TafsirSource.mizan
    ]
    
    comparisons = []
    # البحث في كتالوج المفسرين للحصول على الأسماء والبيانات الأساسية
    from tafsir.resources.catalogs import _TAFSIR_CATALOG
    catalog_map = {item["id"]: item for item in _TAFSIR_CATALOG}
    
    for src in active_sources:
        adapter = ADAPTERS.get(src)
        if not adapter:
            continue
        text = adapter.fetch(ref.surah, ref.ayah)
        if not text:
            continue
            
        cat_info = catalog_map.get(src.value, {})
        display_name = cat_info.get("name_ar", src.value)
        author = cat_info.get("author", "")
        death_year = cat_info.get("death_year_hijri")
        
        school_info = SCHOLAR_SCHOOLS.get(src.value, {
            "theology": "غير متوفر",
            "fiqh": "غير متوفر",
            "method": "تفسير عام"
        })
        
        comparisons.append({
            "source_id": src.value,
            "source_name": display_name,
            "author": author,
            "death_year_hijri": death_year,
            "school_metadata": school_info,
            "text": text
        })
        
    # --- طبقة التحليل البنيوي وتجميع الأقوال (Structural Opinion Layer) ---
    structural_analysis = {
        "agreement": [],
        "fiqh_difference": [],
        "aqeedah_difference": [],
        "linguistic_difference": [],
        "qiraat_difference": [],
        "historical_difference": [],
        "ishari_difference": [],
        "other_opinions": []
    }
    
    disagreement_keywords = ["اختلف", "خلاف", "وقيل", "قيل", "قولان", "مذاهب", "ذهب بعض", "وقال اخر", "وقال اخرون"]
    disagreement_detected = False
    
    for comp in comparisons:
        scholar_id = comp["source_id"]
        scholar_name = comp["source_name"]
        text = comp["text"]
        
        sentences = _split_into_sentences(text)
        for s in sentences:
            dims = _classify_sentence(s)
            
            # التحقق من وجود كلمات تدل على اختلاف في الرأي
            norm_s = _normalize_arabic_simple(s)
            has_disagreement_word = any(dw in norm_s for dw in disagreement_keywords)
            if has_disagreement_word:
                disagreement_detected = True
                
            if dims:
                for d in dims:
                    structural_analysis[d].append({
                        "scholar_id": scholar_id,
                        "scholar_name": scholar_name,
                        "sentence": s
                    })
            elif has_disagreement_word:
                structural_analysis["other_opinions"].append({
                    "scholar_id": scholar_id,
                    "scholar_name": scholar_name,
                    "sentence": s
                })

    guidelines = (
        "أنت الآن خبير مقارنة تفاسير ومناهج مفسرين. قم بتحليل التفاسير المزودة للآية بناءً على الأبعاد التالية:\n"
        "1. نقاط الاتفاق: أين اتفقت الكلمات أو المعنى الإجمالي بين المفسرين؟\n"
        "2. نقاط الاختلاف والتوجيه:\n"
        "   - اختلاف عقدي (Theological): مثل كلام الزمخشري المعتزلي مقارنة بالطبري أو ابن كثير الأثريين، أو الرازي الأشعري.\n"
        "   - اختلاف فقهي (Jurisprudential): الأحكام المستنبطة مثل تركيز القرطبي المالكي مقارنة بالآخرين.\n"
        "   - اختلاف لغوي ونحوي (Linguistic): توجيه الإعراب ومعاني المفردات.\n"
        "   - اختلاف قرائي (Qira'at): أثر القراءات المختلفة في توجيه التفسير.\n"
        "   - اختلاف منهجي (Methodology): هل اعتمد المفسر على الرواية والأثر (بالمأثور) أم العقل والتحليل البلاغي والمقاصدي؟\n"
        "3. سبب الاختلاف: لخص في نقاط موجزة لماذا تباينت وجهات نظرهم للآية."
    )
    
    return {
        "surah": ref.surah,
        "ayah": ref.ayah,
        "ayah_text": ayah_text,
        "comparisons": comparisons,
        "structural_analysis": structural_analysis,
        "disagreement_detected": disagreement_detected,
        "comparison_guidelines": guidelines
    }


def compare_sources(
    source_a: TafsirSource,
    source_b: TafsirSource,
    topic: str | None = None,
) -> dict:
    """مقارنة منهجية وعقدية وفقهية شاملة بين مفسرين اثنين (على مستوى كامل القرآن) مع أمثلة تطبيقية حية.

    source_a: المصدر الأول للمقارنة.
    source_b: المصدر الثاني للمقارنة.
    topic: موضوع اختياري للبحث والمقارنة فيه (مثل: الصفات، المجاز، الوضوء).
    """
    from tafsir.resources.catalogs import _TAFSIR_CATALOG
    catalog_map = {item["id"]: item for item in _TAFSIR_CATALOG}
    
    cat_a = catalog_map.get(source_a.value, {})
    cat_b = catalog_map.get(source_b.value, {})
    
    meta_a = {
        "source_id": source_a.value,
        "name": cat_a.get("name_ar", source_a.value),
        "author": cat_a.get("author", ""),
        "death_year_hijri": cat_a.get("death_year_hijri"),
        "school": SCHOLAR_SCHOOLS.get(source_a.value, {
            "theology": "غير متوفر",
            "fiqh": "غير متوفر",
            "method": "تفسير عام"
        })
    }
    
    meta_b = {
        "source_id": source_b.value,
        "name": cat_b.get("name_ar", source_b.value),
        "author": cat_b.get("author", ""),
        "death_year_hijri": cat_b.get("death_year_hijri"),
        "school": SCHOLAR_SCHOOLS.get(source_b.value, {
            "theology": "غير متوفر",
            "fiqh": "غير متوفر",
            "method": "تفسير عام"
        })
    }
    
    examples = []
    comparison_type = ""
    
    # 1. إذا تم توفير موضوع مخصص، نستخدم الـ FTS5 للبحث عن آيات مشتركة في الشظايا
    if topic and topic.strip():
        comparison_type = f"بحث موضوعي مخصص حول: {topic}"
        # تنظيف موضوع البحث للـ FTS
        import re
        cleaned_topic = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', topic.strip())
        cleaned_topic = re.sub(r'\s+', ' ', cleaned_topic).strip()
        
        from tafsir.adapters.extended import SOURCE_TO_SHARD
        from tafsir.data_loader import get_extended_shard_path
        
        shard_a = SOURCE_TO_SHARD.get(source_a.value)
        shard_b = SOURCE_TO_SHARD.get(source_b.value)
        
        # دالة مساعدة لجلب التطابقات لمصدر معين
        def _get_matches_for_source(source_val, shard_val, q_term):
            matches = []
            if not shard_val: # في quran.db أو jalalayn.db
                from tafsir.data_loader import get_db_path, get_jalalayn_db_path
                import sqlite3
                
                if source_val == "jalalayn":
                    db_p = get_jalalayn_db_path()
                    if db_p.exists():
                        conn = sqlite3.connect(db_p)
                        conn.row_factory = sqlite3.Row
                        try:
                            sql = "SELECT surah, ayah, text FROM tafsir_entries WHERE source_id='jalalayn' AND text LIKE ?"
                            rows = conn.execute(sql, (f"%{q_term}%",)).fetchall()
                            for r in rows:
                                matches.append((r["surah"], r["ayah"], r["text"]))
                        finally:
                            conn.close()
                else:
                    db_p = get_db_path()
                    if db_p.exists():
                        conn = sqlite3.connect(db_p)
                        conn.row_factory = sqlite3.Row
                        try:
                            if source_val in ["tabary", "katheer", "baghawy", "saadi", "moyassar"]:
                                tbl = f"tafsir_{source_val}"
                                sql = f"SELECT sura AS surah, aya AS ayah, tafsir AS text FROM {tbl} WHERE tafsir LIKE ?"
                                rows = conn.execute(sql, (f"%{q_term}%",)).fetchall()
                                for r in rows:
                                                                    matches.append((r["surah"], r["ayah"], r["text"]))
                        finally:
                            conn.close()
            else: # في الشظية الموسعة
                db_p = get_extended_shard_path(shard_val)
                if db_p.exists():
                    import sqlite3
                    conn = sqlite3.connect(db_p)
                    conn.row_factory = sqlite3.Row
                    try:
                        sql = "SELECT surah, ayah, text FROM tafsir_fts WHERE source = ? AND tafsir_fts MATCH ?"
                        rows = conn.execute(sql, (source_val, q_term)).fetchall()
                        for r in rows:
                            matches.append((r["surah"], r["ayah"], r["text"]))
                    except Exception:
                        # Fallback to LIKE
                        sql = "SELECT surah, ayah, text FROM tafsir_content WHERE source = ? AND text LIKE ?"
                        rows = conn.execute(sql, (source_val, f"%{q_term}%")).fetchall()
                        for r in rows:
                            matches.append((r["surah"], r["ayah"], r["text"]))
                    finally:
                        conn.close()
            return matches

        matches_a = _get_matches_for_source(source_a.value, shard_a, cleaned_topic)
        matches_b = _get_matches_for_source(source_b.value, shard_b, cleaned_topic)
        
        # إيجاد التقاطع المشترك للـ (surah, ayah)
        map_b = {(r[0], r[1]): r[2] for r in matches_b}
        
        count = 0
        for surah, ayah, text_a in matches_a:
            if (surah, ayah) in map_b:
                text_b = map_b[(surah, ayah)]
                
                # جلب نص الآية الكريمة
                rasm_rows = query_all(
                    "SELECT word, wordNo FROM word_content_rasm"
                    " WHERE surahNo = ? AND ayahNo = ? ORDER BY wordNo",
                    (surah, ayah),
                )
                ayah_text = reconstruct_ayah(rasm_rows) if rasm_rows else ""
                
                examples.append({
                    "surah": surah,
                    "ayah": ayah,
                    "ayah_text": ayah_text,
                    "commentary_a": text_a[:800] + ("..." if len(text_a) > 800 else ""),
                    "commentary_b": text_b[:800] + ("..." if len(text_b) > 800 else "")
                })
                count += 1
                if count >= 3:
                    break
                    
        if not examples:
            comparison_type += " (لم يتم العثور على آيات مشتركة تحتوي اللفظ بدقة، تم التراجع للآية الافتراضية)"
            
    # 2. إذا لم يتم توفير موضوع أو فشل البحث الموضوعي، نقوم بالربط الآلي بآية محورية ذكية
    if not examples:
        theo_a = meta_a["school"].get("theology", "")
        theo_b = meta_b["school"].get("theology", "")
        fiqh_a = meta_a["school"].get("fiqh", "")
        fiqh_b = meta_b["school"].get("fiqh", "")
        
        # اختيار الآية المحورية الأنسب
        target_surah, target_ayah, target_name = 2, 10, "البلاغة والمجاز واللغة (مرض القلوب)"
        
        if ("معتزلي" in theo_a or "معتزلي" in theo_b or 
            "شيعي" in theo_a or "شيعي" in theo_b or 
            ("أشعر" in theo_a and "أثري" in theo_b) or
            ("أثري" in theo_a and "أشعر" in theo_b)):
            # تباين عقدي قوي -> الاستواء على العرش
            target_surah, target_ayah, target_name = 7, 54, "العقيدة والصفات (الاستواء على العرش - ثم استوى على العرش)"
            comparison_type = "مقارنة عقدية ومنهجية"
        elif ("مالكي" in fiqh_a != "مالكي" in fiqh_b or 
              "شافعي" in fiqh_a != "شافعي" in fiqh_b or 
              "حنفي" in fiqh_a != "حنفي" in fiqh_b or 
              "حنبلي" in fiqh_a != "حنبلي" in fiqh_b):
            # تباين فقهي -> آية الوضوء
            target_surah, target_ayah, target_name = 5, 6, "الأحكام والفقه والعمل (آية الوضوء)"
            comparison_type = "مقارنة فقهية وعملية"
        else:
            comparison_type = "مقارنة عامة وبلاغية"
            
        # جلب تفاسير كلا المفسرين للآية المختارة
        adapter_a = ADAPTERS.get(source_a)
        adapter_b = ADAPTERS.get(source_b)
        
        text_a = adapter_a.fetch(target_surah, target_ayah) if adapter_a else None
        text_b = adapter_b.fetch(target_surah, target_ayah) if adapter_b else None
        
        # جلب نص الآية الكريمة
        rasm_rows = query_all(
            "SELECT word, wordNo FROM word_content_rasm"
            " WHERE surahNo = ? AND ayahNo = ? ORDER BY wordNo",
            (target_surah, target_ayah),
        )
        ayah_text = reconstruct_ayah(rasm_rows) if rasm_rows else ""
        
        if text_a or text_b:
            examples.append({
                "surah": target_surah,
                "ayah": target_ayah,
                "touchpoint_name": target_name,
                "ayah_text": ayah_text,
                "commentary_a": (text_a[:1200] + ("..." if len(text_a) > 1200 else "")) if text_a else "غير متوفر",
                "commentary_b": (text_b[:1200] + ("..." if len(text_b) > 1200 else "")) if text_b else "غير متوفر"
            })
            
    guidelines = (
        f"أنت الآن محقق خبير ومقارن للمذاهب والمناهج الإسلامية. قم بتحليل التباين بين المفسرين:\n"
        f"1. {meta_a['name']} (المؤلف: {meta_a['author']} - الوفاة: {meta_a['death_year_hijri']}هـ) - مدرسته: عقيدة: {meta_a['school']['theology']} / فقه: {meta_a['school']['fiqh']} / منهجه: {meta_a['school']['method']}\n"
        f"2. {meta_b['name']} (المؤلف: {meta_b['author']} - الوفاة: {meta_b['death_year_hijri']}هـ) - مدرسته: عقيدة: {meta_b['school']['theology']} / فقه: {meta_b['school']['fiqh']} / منهجه: {meta_b['school']['method']}\n\n"
        f"استخدم الأمثلة التطبيقية المرفقة لتوضح للمستخدم الفروقات الحية بأسلوب علمي موضوعي حيادي هادئ."
    )
    
    return {
        "source_a": meta_a,
        "source_b": meta_b,
        "comparison_type": comparison_type,
        "examples": examples,
        "comparison_guidelines": guidelines
    }


def register(mcp: FastMCP) -> None:
    mcp.tool(name="fetch_ayah", annotations=_ANNOTATIONS)(get_ayah)
    mcp.tool(name="fetch_tafsir", annotations=_ANNOTATIONS)(get_ayah_tafsir)
    mcp.tool(name="fetch_nuzool_reason", annotations=_ANNOTATIONS)(get_ayah_nuzool)
    mcp.tool(name="deep_ayah_analysis", annotations=_ANNOTATIONS)(get_deep_ayah_analysis)
    mcp.tool(name="compare_tafsir", annotations=_ANNOTATIONS)(compare_tafsir)
    mcp.tool(name="compare_sources", annotations=_ANNOTATIONS)(compare_sources)


