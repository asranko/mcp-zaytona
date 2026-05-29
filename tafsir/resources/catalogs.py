"""MCP Resources: static catalogs and schema documentation."""

import json

from tafsir.db import query_all
from tafsir.models import TAFSIR_ATTRIBUTIONS, TafsirSource

# ── Tafsir catalog (static) ───────────────────────────────────────────────────

_TAFSIR_CATALOG = [
    {
        "id": "tabary",
        "name_ar": "تفسير الإمام الطبري (جامع البيان)",
        "author": "أبو جعفر الطبري",
        "death_year_hijri": 310,
        "db_table": "tafsir_tabary",
        "db_keys": "sura, aya",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.tabary],
    },
    {
        "id": "katheer",
        "name_ar": "تفسير ابن كثير",
        "author": "أبو الفداء إسماعيل بن كثير",
        "death_year_hijri": 774,
        "db_table": "tafsir_katheer",
        "db_keys": "sura, aya",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.katheer],
    },
    {
        "id": "baghawy",
        "name_ar": "تفسير البغوي (معالم التنزيل)",
        "author": "الحسين بن مسعود البغوي",
        "death_year_hijri": 510,
        "db_table": "tafsir_baghawy",
        "db_keys": "sura, aya",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.baghawy],
    },
    {
        "id": "saadi",
        "name_ar": "تيسير الكريم الرحمن (تفسير السعدي)",
        "author": "عبد الرحمن بن ناصر السعدي",
        "death_year_hijri": 1376,
        "db_table": "tafsir_saadi",
        "db_keys": "sura, aya",
        "coverage": "كامل القرآن (6236 آية) — لا قيم فارغة",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.saadi],
    },
    {
        "id": "moyassar",
        "name_ar": "التفسير الميسر",
        "author": "مجمع الملك فهد لطباعة المصحف الشريف",
        "death_year_hijri": None,
        "db_table": "tafsir_moyassar",
        "db_keys": "sura, aya",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.moyassar],
    },
    {
        "id": "mukhtasar_ar",
        "name_ar": "المختصر في تفسير القرآن الكريم",
        "author": "مجمع الملك فهد لطباعة المصحف الشريف",
        "death_year_hijri": None,
        "db_table": "QuranTafseer",
        "db_column": "Mukhtasarar",
        "db_keys": "surahNo, ayahNo",
        "coverage": "كامل القرآن (6236 آية) — لا قيم فارغة",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.mukhtasar_ar],
    },
    {
        "id": "mukhtasar_en",
        "name_ar": "المختصر — ترجمة إنجليزية",
        "name_en": "Concise Quran Commentary (English)",
        "author": "King Fahd Complex for the Printing of the Holy Quran",
        "death_year_hijri": None,
        "db_table": "QuranTafseer",
        "db_column": "Mukhtasaren",
        "db_keys": "surahNo, ayahNo",
        "coverage": "Full Quran (6236 ayahs) — no nulls",
        "language": "en",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.mukhtasar_en],
    },
    {
        "id": "mukhtasar_bn",
        "name_ar": "المختصر — ترجمة بنغالية",
        "name_bn": "সংক্ষিপ্ত তাফসীর (Bengali)",
        "author": "King Fahd Complex for the Printing of the Holy Quran",
        "death_year_hijri": None,
        "db_table": "QuranTafseer",
        "db_column": "Mukhtasarbn",
        "db_keys": "surahNo, ayahNo",
        "coverage": "Full Quran (6236 ayahs) — no nulls",
        "language": "bn",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.mukhtasar_bn],
    },
    {
        "id": "jalalayn",
        "name_ar": "تفسير الجلالين",
        "author": "جلال الدين المحلي + جلال الدين السيوطي",
        "death_year_hijri": 911,
        "db_table": "tafsir_entries",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.jalalayn],
    },
    {
        "id": "tahrir_wa_tanwir",
        "name_ar": "التحرير والتنوير",
        "author": "محمد الطاهر بن عاشور",
        "death_year_hijri": 1393,
        "db_table": "tafsir_tahrir_wa_tanwir",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.tahrir_wa_tanwir],
    },
    {
        "id": "qurtubi",
        "name_ar": "الجامع لأحكام القرآن (تفسير القرطبي)",
        "author": "أبو عبد الله محمد بن أحمد القرطبي",
        "death_year_hijri": 671,
        "db_table": "tafsir_qurtubi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.qurtubi],
    },
    {
        "id": "kashshaf",
        "name_ar": "الكشاف عن حقائق غوامض التنزيل",
        "author": "جار الله الزمخشري",
        "death_year_hijri": 538,
        "db_table": "tafsir_kashshaf",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.kashshaf],
    },
    {
        "id": "mafatih_al_ghayb",
        "name_ar": "مفاتيح الغيب (التفسير الكبير)",
        "author": "فخر الدين الرازي",
        "death_year_hijri": 606,
        "db_table": "tafsir_mafatih_al_ghayb",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.mafatih_al_ghayb],
    },
    {
        "id": "mizan",
        "name_ar": "الميزان في تفسير القرآن",
        "author": "محمد حسين الطباطبائي",
        "death_year_hijri": 1402,
        "db_table": "tafsir_mizan",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.mizan],
    },
    {
        "id": "ruh_al_maani",
        "name_ar": "روح المعاني في تفسير القرآن العظيم",
        "author": "شهاب الدين الألوسي",
        "death_year_hijri": 1270,
        "db_table": "tafsir_ruh_al_maani",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.ruh_al_maani],
    },
    {
        "id": "fath_al_qadir",
        "name_ar": "فتح القدير الجامع بين فني الرواية والدراية",
        "author": "محمد بن علي الشوكاني",
        "death_year_hijri": 1250,
        "db_table": "tafsir_fath_al_qadir",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.fath_al_qadir],
    },
    {
        "id": "adwa_al_bayan",
        "name_ar": "أضواء البيان في إيضاح القرآن بالقرآن",
        "author": "محمد الأمين الشنقيطي",
        "death_year_hijri": 1393,
        "db_table": "tafsir_adwa_al_bayan",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.adwa_al_bayan],
    },
    {
        "id": "sharawi",
        "name_ar": "خواطر محمد متولي الشعراوي",
        "author": "محمد متولي الشعراوي",
        "death_year_hijri": 1418,
        "db_table": "tafsir_sharawi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.sharawi],
    },
    {
        "id": "wasit",
        "name_ar": "التفسير الوسيط",
        "author": "محمد سيد طنطاوي",
        "death_year_hijri": 1431,
        "db_table": "tafsir_wasit",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.wasit],
    },
    {
        "id": "bayani",
        "name_ar": "التفسير البياني للقرآن الكريم",
        "author": "عائشة عبد الرحمن (بنت الشاطئ)",
        "death_year_hijri": 1420,
        "db_table": "tafsir_bayani",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.bayani],
    },
    {
        "id": "fi_zilal",
        "name_ar": "في ظلال القرآن",
        "author": "سيد قطب",
        "death_year_hijri": 1385,
        "db_table": "tafsir_fi_zilal",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.fi_zilal],
    },
    {
        "id": "qushayri",
        "name_ar": "لطائف الإشارات (تفسير القشيري)",
        "author": "عبد الكريم بن هوازن القشيري",
        "death_year_hijri": 465,
        "db_table": "tafsir_qushayri",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.qushayri],
    },
    {
        "id": "ibn_ajiba",
        "name_ar": "البحر المديد في تفسير القرآن المجيد (ابن عجيبة)",
        "author": "أحمد بن عجيبة",
        "death_year_hijri": 1224,
        "db_table": "tafsir_ibn_ajiba",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.ibn_ajiba],
    },
    {
        "id": "nasafi",
        "name_ar": "مدارك التنزيل وحقائق التأويل (تفسير النسفي)",
        "author": "عبد الله بن أحمد النسفي",
        "death_year_hijri": 710,
        "db_table": "tafsir_nasafi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.nasafi],
    },
    {
        "id": "abu_al_saud",
        "name_ar": "إرشاد العقل السليم (تفسير أبي السعود)",
        "author": "محمد بن محمد العمادي أبو السعود",
        "death_year_hijri": 982,
        "db_table": "tafsir_abu_al_saud",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.abu_al_saud],
    },
    {
        "id": "baydawi",
        "name_ar": "أنوار التنزيل وأسرار التأويل (تفسير البيضاوي)",
        "author": "ناصر الدين البيضاوي",
        "death_year_hijri": 685,
        "db_table": "tafsir_baydawi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.baydawi],
    },
    {
        "id": "khazin",
        "name_ar": "لباب التأويل في معاني التنزيل (تفسير الخازن)",
        "author": "علي بن محمد الخازن",
        "death_year_hijri": 741,
        "db_table": "tafsir_khazin",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.khazin],
    },
    {
        "id": "ibn_juzayy",
        "name_ar": "التسهيل لعلوم التنزيل (تفسير ابن جزي)",
        "author": "محمد بن أحمد بن جزي",
        "death_year_hijri": 741,
        "db_table": "tafsir_ibn_juzayy",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.ibn_juzayy],
    },
    {
        "id": "thalabi",
        "name_ar": "الكشف والبيان عن تفسير القرآن (تفسير الثعلبي)",
        "author": "أبو إسحاق الثعلبي",
        "death_year_hijri": 427,
        "db_table": "tafsir_thalabi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.thalabi],
    },
    {
        "id": "mawirdi",
        "name_ar": "النكت والعيون (تفسير الماوردي)",
        "author": "أبو الحسن الماوردي",
        "death_year_hijri": 450,
        "db_table": "tafsir_mawirdi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.mawirdi],
    },
    {
        "id": "samani",
        "name_ar": "تفسير السمعاني",
        "author": "أبو المظفر السمعاني",
        "death_year_hijri": 489,
        "db_table": "tafsir_samani",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.samani],
    },
    {
        "id": "raghib_isfahani",
        "name_ar": "تفسير الراغب الأصفهاني",
        "author": "أبو القاسم الراغب الأصفهاني",
        "death_year_hijri": 502,
        "db_table": "tafsir_raghib_isfahani",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.raghib_isfahani],
    },
    {
        "id": "ibn_atiyya",
        "name_ar": "المحرر الوجيز في تفسير الكتاب العزيز (ابن عطية)",
        "author": "عبد الحق بن غالب ابن عطية",
        "death_year_hijri": 546,
        "db_table": "tafsir_ibn_atiyya",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.ibn_atiyya],
    },
    {
        "id": "zad_al_masir",
        "name_ar": "زاد المسير في علم التفسير (ابن الجوزي)",
        "author": "أبو الفرج ابن الجوزي",
        "death_year_hijri": 597,
        "db_table": "tafsir_zad_al_masir",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.zad_al_masir],
    },
    {
        "id": "bahr_al_muhit",
        "name_ar": "البحر المحيط في التفسير (أبو حيان)",
        "author": "أبو حيان الأندلسي",
        "death_year_hijri": 745,
        "db_table": "tafsir_bahr_al_muhit",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.bahr_al_muhit],
    },
    {
        "id": "samarqandi",
        "name_ar": "بحر العلوم (تفسير السمرقندي)",
        "author": "نصر بن محمد السمرقندي",
        "death_year_hijri": 373,
        "db_table": "tafsir_samarqandi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.samarqandi],
    },
    {
        "id": "ibn_abi_hatim",
        "name_ar": "تفسير ابن أبي حاتم",
        "author": "عبد الرحمن بن محمد ابن أبي حاتم",
        "death_year_hijri": 327,
        "db_table": "tafsir_ibn_abi_hatim",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.ibn_abi_hatim],
    },
    {
        "id": "wahidi_wasit",
        "name_ar": "التفسير الوسيط للواحدي",
        "author": "أبو الحسن الواحدي",
        "death_year_hijri": 468,
        "db_table": "tafsir_wahidi_wasit",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.wahidi_wasit],
    },
    {
        "id": "wahidi_wajiz",
        "name_ar": "الوجيز في تفسير الكتاب العزيز (الواحدي)",
        "author": "أبو الحسن الواحدي",
        "death_year_hijri": 468,
        "db_table": "tafsir_wahidi_wajiz",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.wahidi_wajiz],
    },
    {
        "id": "izz_bin_abd_salam",
        "name_ar": "تفسير العز بن عبد السلام",
        "author": "عبد العزيز بن عبد السلام",
        "death_year_hijri": 660,
        "db_table": "tafsir_izz_bin_abd_salam",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.izz_bin_abd_salam],
    },
    {
        "id": "ibn_rajab",
        "name_ar": "تفسير ابن رجب الحنبلي",
        "author": "عبد الرحمن بن رجب",
        "death_year_hijri": 795,
        "db_table": "tafsir_ibn_rajab",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.ibn_rajab],
    },
    {
        "id": "maturidi",
        "name_ar": "تأويلات أهل السنة (تفسير الماتريدي)",
        "author": "أبو منصور الماتريدي",
        "death_year_hijri": 333,
        "db_table": "tafsir_maturidi",
        "db_keys": "surah, ayah",
        "coverage": "كامل القرآن (6236 آية)",
        "language": "ar",
        "attribution": TAFSIR_ATTRIBUTIONS[TafsirSource.maturidi],
    },
]


def get_surahs_catalog() -> str:
    """JSON catalog of all 114 surahs with key metadata."""
    rows = query_all(
        "SELECT surahNo, surahName, makkiMadani, ayahCount, revelationSeq"
        " FROM surah_stats ORDER BY surahNo"
    )
    data = [
        {
            "surah_no": r["surahNo"],
            "name": r["surahName"],
            "revelation_type": r["makkiMadani"],
            "ayah_count": r["ayahCount"],
            "revelation_order": r["revelationSeq"],
        }
        for r in rows
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def get_tafsirs_catalog() -> str:
    """JSON catalog of all 42 available tafsir sources with full attribution."""
    return json.dumps(_TAFSIR_CATALOG, ensure_ascii=False, indent=2)


def get_schema_documentation() -> str:
    """Developer reference: DB schema, table mapping, key naming conventions."""
    return """\
# Quranic Scholar MCP — Database Schema Reference
> Read-only SQLite 3.x, ~224 MB (includes FTS5 index)

## Key Naming Difference ⚠️
| Tables | Surah column | Ayah column |
|--------|-------------|-------------|
| tafsir_tabary, tafsir_katheer, tafsir_baghawy, tafsir_saadi, tafsir_moyassar | `sura` | `aya` |
| ALL other tables | `surahNo` | `ayahNo` |

## Tables

### Surah-level (114 rows each)
- **surah_stats** — name, revelation type/order, ayah count, word count, statistics
  Columns: id, surahName, surahNo, revelationSeq, makkiMadani, surahClass,
           ayahCount, wordCount, charCount, beginType, longestWord, mostFreqWord, sujud
- **surah_content** — long-form Arabic content
  Columns: surahNo, surahNameInfo, surahNujoolInfo, surahFadael, surahGoals, surahAyahCount0/1

### Tafsir (6236 rows each — one per ayah)
- **tafsir_tabary** — keys: (sura, aya) + id column. Column: tafsir
- **tafsir_katheer** — keys: (sura, aya). Column: tafsir
- **tafsir_baghawy** — keys: (sura, aya). Column: tafsir
- **tafsir_saadi** — keys: (sura, aya). Column: tafsir. Zero NULLs.
- **tafsir_moyassar** — keys: (sura, aya). Column: tafsir
- **QuranTafseer** — keys: (surahNo, ayahNo). Columns: Mukhtasarar (ar), Mukhtasaren (en), Mukhtasarbn (bn). All zero NULLs.

### Ayah-level (6236 rows each)
- **ayah_content_irab** — keys: (surahNo, ayahNo). Column: **irabAyah1** (not 'irab')
- **ayah_content_tajweed** — keys: (surahNo, ayahNo). Column: tajweed
- **ayah_content_nozool** — keys: (surahNo, ayahNo). Column: nozoolInfo
  ⚠️ Only 201 rows (not all ayahs have nuzool info)

### Word-level (77,432 rows each — one per word)
Primary keys across all word tables: (surahNo, ayahNo, wordNo)

- **word_content_rasm** — Columns: id, word (Uthmani text), rasm (note, may be '-')
- **word_content_meaning** — Column: meaning
- **word_content_irab** — Column: **irabMushakkal** (not 'irab')
- **word_content_sarf** — Column: sarf
- **word_statistics** — Columns: root, repeatitionCount (⚠️ typo in DB), rootRepeatitionCount,
  wordNoInSurah, wordNoInAyah, surahCountWithWord, ayahCountWithWord
- **qeraat_info** — Columns: content (@reader/text@ format), note (nullable)
  Multiple rows per ayah; 'no-difference' entries start with 'لا خلاف'

### Page-level
- **mokhtasar_fawaed** — Columns: page (1-604), content
  ⚠️ Multiple rows per page (avg 3.7 per page, 2212 total rows)

### FTS5 (virtual)
- **ayah_fts** — Columns: surahNo UNINDEXED, ayahNo UNINDEXED, text_normalized, text_original
  Tokenizer: unicode61 remove_diacritics 2. Search via: WHERE text_normalized MATCH ?

## Ayah Text Reconstruction
Full ayah text = concatenate word_content_rasm.word ORDER BY wordNo for given (surahNo, ayahNo).
Includes disconnected letters (e.g., 'الم' is wordNo=1 only).

## Row Counts (verified)
| Table | Rows |
|-------|------|
| surah_stats / surah_content | 114 |
| all tafsir tables | 6236 each |
| QuranTafseer | 6236 |
| ayah_content_irab / tajweed | 6236 each |
| ayah_content_nozool | 201 |
| word_content_* / word_statistics / qeraat_info | 77,432 each |
| mokhtasar_fawaed | 2212 |
| ayah_fts | 6236 |
"""
