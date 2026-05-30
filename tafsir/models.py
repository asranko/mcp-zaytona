"""Pydantic v2 response models for Quranic Scholar MCP."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

# عدد آيات كل سورة — مستخرج من surah_stats
SURAH_AYAH_COUNTS: dict[int, int] = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129,
    10: 109, 11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111,
    18: 110, 19: 98, 20: 135, 21: 112, 22: 78, 23: 118, 24: 64, 25: 77,
    26: 227, 27: 93, 28: 88, 29: 69, 30: 60, 31: 34, 32: 30, 33: 73,
    34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85, 41: 54,
    42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18,
    50: 45, 51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29,
    58: 22, 59: 24, 60: 13, 61: 14, 62: 11, 63: 11, 64: 18, 65: 12,
    66: 12, 67: 30, 68: 52, 69: 52, 70: 44, 71: 28, 72: 28, 73: 20,
    74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42, 81: 29,
    82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30,
    90: 20, 91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5,
    98: 8, 99: 8, 100: 11, 101: 11, 102: 8, 103: 3, 104: 9, 105: 5,
    106: 4, 107: 7, 108: 3, 109: 6, 110: 3, 111: 5, 112: 4, 113: 5,
    114: 6,
}


class TafsirSource(StrEnum):
    tabary = "tabary"
    katheer = "katheer"
    baghawy = "baghawy"
    saadi = "saadi"
    moyassar = "moyassar"
    mukhtasar_ar = "mukhtasar_ar"
    mukhtasar_en = "mukhtasar_en"
    mukhtasar_bn = "mukhtasar_bn"
    jalalayn = "jalalayn"
    tahrir_wa_tanwir = "tahrir_wa_tanwir"
    qurtubi = "qurtubi"
    kashshaf = "kashshaf"
    mafatih_al_ghayb = "mafatih_al_ghayb"
    mizan = "mizan"
    ruh_al_maani = "ruh_al_maani"
    fath_al_qadir = "fath_al_qadir"
    adwa_al_bayan = "adwa_al_bayan"
    sharawi = "sharawi"
    wasit = "wasit"
    bayani = "bayani"
    fi_zilal = "fi_zilal"
    qushayri = "qushayri"
    ibn_ajiba = "ibn_ajiba"
    nasafi = "nasafi"
    abu_al_saud = "abu_al_saud"
    baydawi = "baydawi"
    khazin = "khazin"
    ibn_juzayy = "ibn_juzayy"
    thalabi = "thalabi"
    mawirdi = "mawirdi"
    samani = "samani"
    raghib_isfahani = "raghib_isfahani"
    ibn_atiyya = "ibn_atiyya"
    zad_al_masir = "zad_al_masir"
    bahr_al_muhit = "bahr_al_muhit"
    samarqandi = "samarqandi"
    ibn_abi_hatim = "ibn_abi_hatim"
    wahidi_wasit = "wahidi_wasit"
    wahidi_wajiz = "wahidi_wajiz"
    izz_bin_abd_salam = "izz_bin_abd_salam"
    ibn_rajab = "ibn_rajab"
    maturidi = "maturidi"
    durr_manthur = "durr_manthur"
    nazm_durar = "nazm_durar"
    ghareeb_quran = "ghareeb_quran"
    gharaib_quran = "gharaib_quran"
    tadhkirat_areeb = "tadhkirat_areeb"
    durr_masun = "durr_masun"
    lubab_ulum = "lubab_ulum"
    manar = "manar"
    safwat = "safwat"
    asbab_nuzul = "asbab_nuzul"
    ayat_ahkam = "ayat_ahkam"
    aysar_jazairi = "aysar_jazairi"
    aysar_homod = "aysar_homod"
    burhan_bahrani = "burhan_bahrani"
    tawilat_najmiyya = "tawilat_najmiyya"
    tibyan_tusi = "tibyan_tusi"
    tabarani = "tabarani"
    ibn_arafa = "ibn_arafa"
    jawahir_thaalbi = "jawahir_thaalbi"
    safi_kashani = "safi_kashani"
    sirat_mustaqim = "sirat_mustaqim"
    muntakhab = "muntakhab"
    nahr_madd = "nahr_madd"
    aaqam = "aaqam"
    jilani = "jilani"
    hubari = "hubari"
    ibn_arabi = "ibn_arabi"
    ibn_abi_zamnin = "ibn_abi_zamnin"
    tustari = "tustari"
    fairuzabadi = "fairuzabadi"
    qummi = "qummi"
    nasai = "nasai"
    hidayah_maki = "hidayah_maki"
    bayan_saadah = "bayan_saadah"
    sufyan_thawri = "sufyan_thawri"
    sadr_mutaallhin = "sadr_mutaallhin"
    abd_razzaq = "abd_razzaq"
    furat_kufi = "furat_kufi"
    hawari = "hawari"
    mujahid = "mujahid"
    taysir_atfiyyish = "taysir_atfiyyish"
    taysir_qattan = "taysir_qattan"
    jawahir_khalili = "jawahir_khalili"
    hashiyat_sawi = "hashiyat_sawi"
    haqaiq_sulami = "haqaiq_sulami"
    rumuz_kunuz = "rumuz_kunuz"
    ruh_bayan = "ruh_bayan"
    araais_bayan = "araais_bayan"
    nuzhat_qulub = "nuzhat_qulub"
    majma_bayan = "majma_bayan"
    mahasin_tawil = "mahasin_tawil"
    mukhtasar_katheer = "mukhtasar_katheer"
    muqatil = "muqatil"
    himyan_zad = "himyan_zad"


TAFSIR_ATTRIBUTIONS: dict[TafsirSource, str] = {
    TafsirSource.tabary:         "تفسير الإمام الطبري (جامع البيان)، أبو جعفر الطبري (ت. 310هـ)",
    TafsirSource.katheer:        "تفسير ابن كثير، أبو الفداء إسماعيل بن كثير (ت. 774هـ)",
    TafsirSource.baghawy:        "تفسير البغوي (معالم التنزيل)، الحسين بن مسعود البغوي (ت. 510هـ)",
    TafsirSource.saadi:          "تيسير الكريم الرحمن، عبد الرحمن بن ناصر السعدي (ت. 1376هـ)",
    TafsirSource.moyassar:       "التفسير الميسر، مجمع الملك فهد لطباعة المصحف الشريف",
    TafsirSource.mukhtasar_ar:   "المختصر في تفسير القرآن الكريم (عربي)",
    TafsirSource.mukhtasar_en:   "Concise Quran Commentary (English)",
    TafsirSource.mukhtasar_bn:   "সংক্ষিপ্ত তাফসীর (Bengali)",
    TafsirSource.jalalayn:       "تفسير الجلالين، جلال الدين المحلي (ت. 864هـ) وجلال الدين السيوطي (ت. 911هـ)",
    TafsirSource.tahrir_wa_tanwir: "التحرير والتنوير، محمد الطاهر بن عاشور (ت. 1393هـ)",
    TafsirSource.qurtubi:        "الجامع لأحكام القرآن، أبو عبد الله محمد بن أحمد القرطبي (ت. 671هـ)",
    TafsirSource.kashshaf:       "الكشاف عن حقائق غوامض التنزيل، جار الله الزمخشري (ت. 538هـ)",
    TafsirSource.mafatih_al_ghayb: "مفاتيح الغيب (التفسير الكبير)، فخر الدين الرازي (ت. 606هـ)",
    TafsirSource.mizan:          "الميزان في تفسير القرآن، محمد حسين الطباطبائي (ت. 1402هـ)",
    TafsirSource.ruh_al_maani:   "روح المعاني في تفسير القرآن العظيم، شهاب الدين الألوسي (ت. 1270هـ)",
    TafsirSource.fath_al_qadir:  "فتح القدير الجامع بين فني الرواية والدراية، محمد بن علي الشوكاني (ت. 1250هـ)",
    TafsirSource.adwa_al_bayan:  "أضواء البيان في إيضاح القرآن بالقرآن، محمد الأمين الشنقيطي (ت. 1393هـ)",
    TafsirSource.sharawi:        "خواطر محمد متولي الشعراوي، محمد متولي الشعراوي (ت. 1418هـ)",
    TafsirSource.wasit:          "التفسير الوسيط، محمد سيد طنطاوي (ت. 1431هـ)",
    TafsirSource.bayani:         "التفسير البياني للقرآن الكريم، عائشة عبد الرحمن (بنت الشاطئ) (ت. 1420هـ)",
    TafsirSource.fi_zilal:       "في ظلال القرآن، سيد قطب (ت. 1385هـ)",
    TafsirSource.qushayri:       "لطائف الإشارات، عبد الكريم بن هوازن القشيري (ت. 465هـ)",
    TafsirSource.ibn_ajiba:      "البحر المديد في تفسير القرآن المجيد، أحمد بن عجيبة (ت. 1224هـ)",
    TafsirSource.nasafi:         "مدارك التنزيل وحقائق التأويل، عبد الله بن أحمد النسفي (ت. 710هـ)",
    TafsirSource.abu_al_saud:    "إرشاد العقل السليم إلى مزايا الكتاب الكريم، أبو السعود العمادي (ت. 982هـ)",
    TafsirSource.baydawi:        "أنوار التنزيل وأسرار التأويل، ناصر الدين البيضاوي (ت. 685هـ)",
    TafsirSource.khazin:         "لباب التأويل في معاني التنزيل، علي بن محمد الخازن (ت. 741هـ)",
    TafsirSource.ibn_juzayy:     "التسهيل لعلوم التنزيل، محمد بن أحمد بن جزي (ت. 741هـ)",
    TafsirSource.thalabi:        "الكشف والبيان عن تفسير القرآن، أبو إسحاق الثعلبي (ت. 427هـ)",
    TafsirSource.mawirdi:        "النكت والعيون (تفسير الماوردي)، أبو الحسن الماوردي (ت. 450هـ)",
    TafsirSource.samani:         "تفسير السمعاني، أبو المظفر السمعاني (ت. 489هـ)",
    TafsirSource.raghib_isfahani: "تفسير الراغب الأصفهاني، أبو القاسم الراغب الأصفهاني (ت. 502هـ)",
    TafsirSource.ibn_atiyya:     "المحرر الوجيز في تفسير الكتاب العزيز، عبد الحق بن غالب ابن عطية (ت. 546هـ)",
    TafsirSource.zad_al_masir:   "زاد المسير في علم التفسير، أبو الفرج ابن الجوزي (ت. 597هـ)",
    TafsirSource.bahr_al_muhit:  "البحر المحيط في التفسير، أبو حيان الأندلسي (ت. 745هـ)",
    TafsirSource.samarqandi:     "بحر العلوم (تفسير السمرقندي)، نصر بن محمد السمرقندي (ت. 373هـ)",
    TafsirSource.ibn_abi_hatim:  "تفسير ابن أبي حاتم، عبد الرحمن بن محمد ابن أبي حاتم (ت. 327هـ)",
    TafsirSource.wahidi_wasit:   "التفسير الوسيط للواحدي، أبو الحسن الواحدي (ت. 468هـ)",
    TafsirSource.wahidi_wajiz:   "الوجيز في تفسير الكتاب العزيز، أبو الحسن الواحدي (ت. 468هـ)",
    TafsirSource.izz_bin_abd_salam: "تفسير العز بن عبد السلام، عبد العزيز بن عبد السلام (ت. 660هـ)",
    TafsirSource.ibn_rajab:      "تفسير ابن رجب الحنبلي، عبد الرحمن بن رجب (ت. 795هـ)",
    TafsirSource.maturidi:       "تأويلات أهل السنة (تفسير الماتريدي)، أبو منصور الماتريدي (ت. 333هـ)",
    TafsirSource.durr_manthur:    "تفسير الدر المنثور في التفسير بالمأثور، جلال الدين السيوطي (ت. 911هـ)",
    TafsirSource.nazm_durar:      "نظم الدرر في تناسب الآيات والسور، برهان الدين البقاعي (ت. 885هـ)",
    TafsirSource.ghareeb_quran:   "تفسير غريب القرآن، زيد بن علي (ت. 120هـ)",
    TafsirSource.gharaib_quran:   "غرائب القرآن ورغائب الفرقان، نظام الدين النيسابوري (ت. 728هـ)",
    TafsirSource.tadhkirat_areeb: "تذكرة الأريب في تفسير الغريب، أبو الفرج ابن الجوزي (ت. 597هـ)",
    TafsirSource.durr_masun:      "الدر المصون في علوم الكتاب المكنون، السمين الحلبي (ت. 756هـ)",
    TafsirSource.lubab_ulum:      "اللباب في علوم الكتاب، ابن عادل الحنبلي (ت. 880هـ)",
    TafsirSource.manar:           "تفسير المنار، محمد رشيد رضا (ت. 1354هـ)",
    TafsirSource.safwat:          "صفوة التفاسير، محمد علي الصابوني (ت. 1442هـ / 2021م)",
    TafsirSource.asbab_nuzul:     "صحيح أسباب النزول دراسة حديثية، إبراهيم محمد العلي (مؤلف معاصر)",
    TafsirSource.ayat_ahkam: "روائع البيان في تفسير آيات الأحكام، محمد علي الصابوني",
    TafsirSource.aysar_jazairi: "أيسر التفاسير لكلام العلي الكبير، أبو بكر الجزائري",
    TafsirSource.aysar_homod: "أيسر التفاسير، د. أسعد حومد",
    TafsirSource.burhan_bahrani: "البرهان في تفسير القرآن، السيد هاشم البحراني",
    TafsirSource.tawilat_najmiyya: "التأويلات النجمية في التفسير الإشاري الصوفي، أحمد بن عمر النجم الدين كبرى",
    TafsirSource.tibyan_tusi: "التبيان في تفسير القرآن، الشيخ الطوسي",
    TafsirSource.tabarani: "التفسير الكبير، الإمام الطبراني",
    TafsirSource.ibn_arafa: "تفسير ابن عرفة، أبو عبد الله محمد بن عرفة الورغمي",
    TafsirSource.jawahir_thaalbi: "الجواهر الحسان في تفسير القرآن، عبد الرحمن الثعالبي",
    TafsirSource.safi_kashani: "التفسير الصافي، الفيض الكاشاني",
    TafsirSource.sirat_mustaqim: "الصراط المستقيم في تبيان القرآن الكريم (تفسير الكازروني)",
    TafsirSource.muntakhab: "المنتخب في تفسير القرآن الكريم، المجلس الأعلى للشؤون الإسلامية بمصر",
    TafsirSource.nahr_madd: "النهر الماد من البحر المحيط، أبو حيان الأندلسي",
    TafsirSource.aaqam: "تفسير الأعقم، محمد بن شرف الدين الأعقم",
    TafsirSource.jilani: "تفسير الجيلاني، عبد القادر الجيلاني",
    TafsirSource.hubari: "تفسير الحبري، الحسين بن الحكم الحبري",
    TafsirSource.ibn_arabi: "تفسير ابن عربي، محيي الدين بن عربي",
    TafsirSource.ibn_abi_zamnin: "تفسير القرآن العزيز، ابن أبي زمنين",
    TafsirSource.tustari: "تفسير التستري، سهل بن عبد الله التستري",
    TafsirSource.fairuzabadi: "تنوير المقباس من تفسير ابن عباس (تفسير الفيروز آبادي)",
    TafsirSource.qummi: "تفسير القمي، علي بن إبراهيم القمي",
    TafsirSource.nasai: "تفسير النسائي، الإمام النسائي",
    TafsirSource.hidayah_maki: "الهداية إلى بلوغ النهاية، مكي بن أبي طالب القيسي",
    TafsirSource.bayan_saadah: "بيان السعادة في مقامات العبادة، سلطان محمد الجنابذي",
    TafsirSource.sufyan_thawri: "تفسير سفيان الثوري، سفيان بن سعيد الثوري",
    TafsirSource.sadr_mutaallhin: "تفسير صدر المتألهين، ملا صدرا الشيرازي",
    TafsirSource.abd_razzaq: "تفسير عبد الرزاق، عبد الرزاق الصنعاني",
    TafsirSource.furat_kufi: "تفسير فرات الكوفي، فرات بن إبراهيم الكوفي",
    TafsirSource.hawari: "تفسير كتاب الله العزيز، هود بن محكم الهواري",
    TafsirSource.mujahid: "تفسير مجاهد، مجاهد بن جبر المخزومي",
    TafsirSource.taysir_atfiyyish: "تيسير التفسير، محمد بن يوسف أطفيش",
    TafsirSource.taysir_qattan: "تيسير التفسير، أحمد مصطفى القطان",
    TafsirSource.jawahir_khalili: "جواهر التفسير أنوار من بيان التنزيل، أحمد بن حمد الخليلي",
    TafsirSource.hashiyat_sawi: "حاشية الصاوي على تفسير الجلالين، أحمد بن محمد الصاوي",
    TafsirSource.haqaiq_sulami: "حقائق التفسير، أبو عبد الرحمن السلمي",
    TafsirSource.rumuz_kunuz: "رموز الكنوز في تفسير الكتاب العزيز، عز الدين الرسعني",
    TafsirSource.ruh_bayan: "روح البيان، إسماعيل حقي البروسوي",
    TafsirSource.araais_bayan: "عرائس البيان في حقائق القرآن، روزبهان البقلي الشيرازي",
    TafsirSource.nuzhat_qulub: "نزهة القلوب في تفسير غريب القرآن، أبو بكر السجستاني",
    TafsirSource.majma_bayan: "مجمع البيان في تفسير القرآن، الشيخ الطبرسي",
    TafsirSource.mahasin_tawil: "محاسن التأويل، جمال الدين القاسمي",
    TafsirSource.mukhtasar_katheer: "مختصر تفسير ابن كثير، محمد علي الصابوني",
    TafsirSource.muqatil: "تفسير مقاتل بن سليمان، مقاتل بن سليمان البلخي",
    TafsirSource.himyan_zad: "هميان الزاد إلى دار المعاد، محمد بن يوسف أطفيش",
}


class AyahReference(BaseModel):
    surah: int = Field(ge=1, le=114, description="رقم السورة")
    ayah: int = Field(ge=1, description="رقم الآية")

    @model_validator(mode="after")
    def ayah_within_surah_bounds(self) -> "AyahReference":
        max_ayah = SURAH_AYAH_COUNTS[self.surah]
        if self.ayah > max_ayah:
            raise ValueError(
                f"السورة {self.surah} تحتوي على {max_ayah} آية فقط، "
                f"الرقم المُدخل {self.ayah} خارج النطاق."
            )
        return self


class AyahResponse(BaseModel):
    surah: int
    ayah: int
    text: str
    tajweed: str | None = None
    irab: str | None = None
    word_count: int


class TafsirEntry(BaseModel):
    source: TafsirSource
    attribution: str
    text: str


class TafsirResponse(BaseModel):
    surah: int
    ayah: int
    tafsirs: list[TafsirEntry]


class WordAnalysis(BaseModel):
    word_no: int
    word: str
    meaning: str | None = None
    irab: str | None = None
    sarf: str | None = None
    root: str | None = None
    frequency: int | None = None


class SurahInfo(BaseModel):
    surah_no: int
    names: list[str]
    revelation_type: str
    ayah_count: int
    revelation_order: int
    virtues: str | None
    objectives: str | None
    statistics: dict[str, Any]
