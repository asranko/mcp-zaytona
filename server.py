# -*- coding: utf-8 -*-
"""
خادم الزيتونة المعرفي ثنائي البروتوكول (Zaytona Dual-Protocol Server)
-------------------------------------------------------------------
خادم متطور يدعم بروتوكولين في نفس الوقت:
1. بروتوكول MCP (Model Context Protocol) للتكامل مع Claude Desktop.
2. بروتوكول REST API (واجهة برمجة التطبيقات) للتكامل مع إجراءات ChatGPT (Custom GPT Actions).

تمت ترقيته ليرتبط بقاعدة بيانات التفاسير الكلاسيكية والموسعة بالكامل (18 تفسيراً كبيراً)
بالتنسيق مع مكتبة ومستودع Tafsir MCP المحلي.
"""

from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import os
import sys
import re

# تهيئة نظام الترميز الافتراضي لـ UTF-8 لتفادي مشاكل الحروف العربية على ويندوز
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# إضافة مسار مجلد السيرفر لضمان استخدام حزمة tafsir المدمجة محلياً أولاً سحابياً ومحلياً
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# إضافة مسار مكتبة التفسير محلياً الاحتياطي إذا كان متوفراً
TAFSIR_MCP_SRC = "C:\\Users\\moasran\\Desktop\\tafser\\tafsir-mcp\\src"
if os.path.exists(TAFSIR_MCP_SRC) and TAFSIR_MCP_SRC not in sys.path:
    sys.path.append(TAFSIR_MCP_SRC)

# 1. تعريف خادم FastMCP الأساسي لـ Claude
mcp = FastMCP("Zaytona")

# تسجيل أدوات وموارد وقوالب التفسير بالكامل داخل خادم الزيتونة
try:
    from tafsir.tools import ayah as ayah_tools
    from tafsir.tools import surah as surah_tools
    from tafsir.tools import word as word_tools
    from tafsir.tools import qeraat as qeraat_tools
    from tafsir.tools import search as search_tools
    from tafsir.tools import stats as stats_tools
    from tafsir.tools import lexicon as lexicon_tools
    from tafsir.tools.ayah import get_ayah_tafsir, get_ayah, get_deep_ayah_analysis
    from tafsir.tools.search import search_quran_text
    
    # تسجيل الأدوات
    ayah_tools.register(mcp)
    surah_tools.register(mcp)
    word_tools.register(mcp)
    lexicon_tools.register(mcp)
    qeraat_tools.register(mcp)
    search_tools.register(mcp)
    stats_tools.register(mcp)
    
    # تسجيل الموارد
    from tafsir.resources import catalogs
    @mcp.resource("quran://surahs")
    def surahs_catalog() -> str:
        """فهرس 114 سورة مع البيانات الأساسية (JSON)."""
        return catalogs.get_surahs_catalog()

    @mcp.resource("quran://tafsirs")
    def tafsirs_catalog() -> str:
        """فهرس 42 مصدراً تفسيرياً مع كامل بيانات الإسناد (JSON)."""
        return catalogs.get_tafsirs_catalog()

    @mcp.resource("quran://schema")
    def schema_documentation() -> str:
        """مرجع مخطط قاعدة البيانات للمطورين (Markdown)."""
        return catalogs.get_schema_documentation()

    # تسجيل القوالب
    from tafsir.prompts import study as study_prompts
    study_prompts.register(mcp)
    
    print("✅ تم ربط جميع أدوات وموارد وقوالب التفسير المتقدمة بنجاح!")
except Exception as e:
    print(f"⚠️ فشل ربط أدوات أو موارد أو قوالب التفسير بخادم الزيتونة: {e}")


@mcp.tool(
    name="extract_zaytona",
    description="تحليل النصوص واستخراج الزيتونة المعرفية بصيغة ثلاثية: المبدأ، التطبيق، والأثر."
)
def extract_zaytona(text: str) -> dict:
    """
    يقوم باستقبال نص طويل أو مقال، ويعيد صياغته كـ كبسولة معرفية مضغوطة (مبدأ -> تطبيق -> أثر).
    
    إذا كان النص يحتوي على مرجع لآية قرآنية (مثل 2:255)، فإنه يقوم تلقائياً بدمج تفسيرها لاستخلاص الزيتونة.
    """
    if not text or not text.strip():
        return {
            "principle": "لا يوجد نص كافٍ لاستخلاص المبدأ.",
            "application": "يرجى تزويد الأداة بنص يحتوي على فكرة أو سياق متكامل.",
            "effect": "فشل الاستخلاص بسبب غياب البيانات المدخلة."
        }
    
    # محاولة فك ترميز مرجع الآية إذا كان موجوداً
    match = re.search(r"(\d+)\s*[:：]\s*(\d+)", text)
    if match:
        try:
            s = int(match.group(1))
            a = int(match.group(2))
            from tafsir.models import SURAH_AYAH_COUNTS
            if 1 <= s <= 114 and 1 <= a <= SURAH_AYAH_COUNTS.get(s, 286):
                # جلب نص الآية وتفسير السعدي كمرجع
                ayah_data = get_ayah(s, a)
                tafsir_data = get_ayah_tafsir(s, a, ["saadi", "katheer"])
                
                ayah_text = ayah_data.get("text", "")
                saadi_text = ""
                katheer_text = ""
                for entry in tafsir_data.get("tafsirs", []):
                    if entry["source"] == "saadi":
                        saadi_text = entry["text"]
                    elif entry["source"] == "katheer":
                        katheer_text = entry["text"]
                
                return {
                    "principle": f"الآية الكريمة: {{{ayah_text}}} [سورة {s} آية {a}]",
                    "application": f"تفسير السعدي: {saadi_text[:400]}...",
                    "effect": f"تفسير ابن كثير: {katheer_text[:400]}..."
                }
        except Exception:
            pass
        
    return {
        "principle": "المبدأ الجوهري المستخرج (Principle): [سيتم ملؤه ديناميكياً بواسطة النموذج بناءً على تحليل النص المدخل]",
        "application": "التطبيق العملي الفعلي (Application): [خطوات توظيف المبدأ في مساحة عمل حقيقية]",
        "effect": "الأثر المتوقع والنتيجة (Effect): [الفائدة العائدة والصلابة المحققة]"
    }

@mcp.tool(
    name="extract_zaytona_from_ayah",
    description="استخراج الزيتونة المعرفية مباشرة لآية معينة بالاعتماد على تفسير السعدي وابن كثير والقرطبي."
)
def extract_zaytona_from_ayah(surah: int, ayah: int) -> dict:
    """
    يجلب نص الآية الكريمة وتفسيرها من المصادر، ويقدم هيكلية مناسبة للنموذج لاستخلاص كبسولة الزيتونة.
    """
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if not (1 <= surah <= 114) or ayah > SURAH_AYAH_COUNTS.get(surah, 286):
            return {"error": "رقم السورة أو الآية خارج الحدود المسموحة."}
            
        ayah_data = get_ayah(surah, ayah)
        tafsir_data = get_ayah_tafsir(surah, ayah, ["saadi", "katheer", "qurtubi"])
        
        return {
            "surah": surah,
            "ayah": ayah,
            "ayah_text": ayah_data.get("text", ""),
            "tafsirs": [
                {
                    "attribution": t["attribution"],
                    "text": t["text"][:1000] + ("..." if len(t["text"]) > 1000 else "")
                } for t in tafsir_data.get("tafsirs", [])
            ],
            "_display_instructions": "أنت الآن ريكي الشريك المعرفي. استنبط من هذه الآية وتفاسيرها كبسولة الزيتونة الثلاثية: المبدأ الجوهري العام، التطبيق العملي الواقعي، والأثر الروحي والعملي المتوقع."
        }
    except Exception as e:
        return {"error": f"فشل استخراج الزيتونة للآية: {e}"}


# تهيئة تطبيق FastMCP HTTP والحصول على lifespan الخاص به
# هذا ضروري لتفادي خطأ "Task group is not initialized" عند التشغيل
try:
    mcp_http = mcp.http_app()
    mcp_lifespan = mcp_http.lifespan
except Exception as e:
    print(f"⚠️ فشل تهيئة تطبيق MCP HTTP: {e}")
    mcp_http = None
    mcp_lifespan = None

# 2. تعريف خادم FastAPI المخصص لـ ChatGPT
app = FastAPI(
    title="Zaytona API",
    description="API to extract the core cognitive capsule (Principle, Application, Effect) from any text, integrated with classical Islamic Tafsirs.",
    version="1.1.0",
    lifespan=mcp_lifespan
)

# تفعيل CORS Middleware لضمان السماح لـ ChatGPT بالاتصال بالخادم والتحقق منه دون مشاكل
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Zaytona API",
        version="1.1.0",
        description="API to extract the core cognitive capsule (Principle, Application, Effect) from any text, integrated with classical Islamic Tafsirs.",
        routes=app.routes,
    )
    # إجبار مواصفات OpenAPI على الإصدار 3.1.0 المتوافق تماماً مع متطلبات ChatGPT الحديثة
    openapi_schema["openapi"] = "3.1.0"
    openapi_schema["servers"] = [
        {
            "url": "https://zaytona-mcp.onrender.com",
            "description": "Zaytona Production Server"
        }
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    principle: str
    application: str
    effect: str

class DeepAnalysisRequest(BaseModel):
    surah: int = Field(ge=1, le=114, description="رقم السورة من 1 إلى 114")
    ayah: int = Field(ge=1, description="رقم الآية في السورة")
    sources: list[str] | None = Field(default=None, description="قائمة اختيارية بكتب التفسير المطلوبة")

class TafsirRequest(BaseModel):
    surah: int = Field(ge=1, le=114)
    ayah: int = Field(ge=1)
    sources: list[str] | None = None

class AyahRequest(BaseModel):
    surah: int = Field(ge=1, le=114)
    ayah: int = Field(ge=1)
    include: list[str] | None = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SurahRequest(BaseModel):
    surah: int = Field(ge=1, le=114, description="رقم السورة من 1 إلى 114")

class WordRequest(BaseModel):
    surah: int = Field(ge=1, le=114, description="رقم السورة من 1 إلى 114")
    ayah: int = Field(ge=1, description="رقم الآية في السورة")
    word_no: int = Field(ge=1, description="رقم الكلمة في الآية (يبدأ من 1)")
    aspects: list[str] | None = Field(default=None, description="الطبقات التحليلية المطلوبة: meaning, irab, sarf, statistics, qeraat")

class RootOccurrencesRequest(BaseModel):
    root: str = Field(description="الجذر اللغوي للبحث (مثال: رحم، كتب)")
    limit: int = Field(default=50, ge=1, le=500, description="الحد الأقصى لعدد النتائج")

class RootStatsRequest(BaseModel):
    root: str = Field(description="الجذر اللغوي المراد عرض إحصائياته (مثال: رحم، كتب)")

class RootDefinitionRequest(BaseModel):
    root: str = Field(description="الجذر اللغوي للبحث عنه في المعاجم (مثال: رحم، كتب)")

class QeraatRequest(BaseModel):
    surah: int = Field(ge=1, le=114, description="رقم السورة من 1 إلى 114")
    ayah: int = Field(ge=1, description="رقم الآية في السورة")
    word_no: int | None = Field(default=None, description="رقم الكلمة اختيارياً لعرض قراءات كلمة معينة")

class NuzoolRequest(BaseModel):
    surah: int = Field(ge=1, le=114, description="رقم السورة من 1 إلى 114")
    ayah: int = Field(ge=1, description="رقم الآية في السورة")

class PageRequest(BaseModel):
    page: int = Field(ge=1, le=604, description="رقم صفحة المصحف من 1 إلى 604")

class TafsirSearchRequest(BaseModel):
    query: str = Field(description="نص البحث المراد البحث عنه في التفاسير")
    source: str = Field(default="saadi", description="رمز التفسير المختار (مثال: saadi, katheer, qurtubi, sharawi, tabary)")
    surah_filter: list[int] | None = Field(default=None, description="قائمة اختيارية بأرقام السور لتصفية نتائج البحث")
    limit: int = Field(default=20, ge=1, le=100, description="الحد الأقصى لعدد النتائج")

@app.get("/", summary="مخطط OpenAPI المباشر", include_in_schema=False)
def root_endpoint():
    # إرجاع مخطط OpenAPI مباشرة لتسهيل الربط في ChatGPT بالرابط الأساسي للسيرفر فقط دون أي مسارات إضافية
    return app.openapi()

@app.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract Cognitive Capsule",
    description="Extracts the core principle, application, and effect from the given text or Quranic ayah."
)
def extract_api(request: ExtractRequest):
    """
    نقطة اتصال REST API مخصصة لاستقبال النصوص وإرجاع الزيتونة المعرفية مباشرة لـ ChatGPT.
    يدعم التعرف التلقائي على الآيات وجلب تفسيرها.
    """
    result = extract_zaytona(request.text)
    return ExtractResponse(
        principle=result["principle"],
        application=result["application"],
        effect=result["effect"]
    )

@app.post(
    "/tafsir",
    summary="Get Tafsir from Classical Databases",
    description="Fetches tafsir text for a specific surah and ayah from classical books including Qurtubi, Ibn Kathir, Al-Razi, Tabari, etc."
)
def get_tafsir_api(request: TafsirRequest):
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if request.ayah > SURAH_AYAH_COUNTS.get(request.surah, 286):
            raise HTTPException(status_code=400, detail="رقم الآية خارج حدود السورة")
        
        result = get_ayah_tafsir(request.surah, request.ayah, request.sources)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/ayah",
    summary="Get Ayah Text",
    description="Gets the verbatim Uthmani script text of any ayah, with optional tajweed rules or grammatical i'rab."
)
def get_ayah_api(request: AyahRequest):
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if request.ayah > SURAH_AYAH_COUNTS.get(request.surah, 286):
            raise HTTPException(status_code=400, detail="رقم الآية خارج حدود السورة")
        
        result = get_ayah(request.surah, request.ayah, request.include)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/ayah/deep-analysis",
    summary="Get Deep Ayah Analysis",
    description="Fetches an integrated Qur'an research capsule for any ayah including verbatim text, selected tafsirs, full word-by-word linguistic analysis (meaning, grammar, morphology, roots, frequencies), causes of revelation, qeraat variants, and structured cognitive extraction guidelines."
)
def get_deep_ayah_analysis_api(request: DeepAnalysisRequest):
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if request.ayah > SURAH_AYAH_COUNTS.get(request.surah, 286):
            raise HTTPException(status_code=400, detail="رقم الآية خارج حدود السورة")
        
        result = get_deep_ayah_analysis(request.surah, request.ayah, request.sources)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/search",
    summary="Search Quran Text",
    description="Performs an FTS5 search inside the entire Holy Quran text."
)
def search_api(request: SearchRequest):
    try:
        result = search_quran_text(request.query, limit=request.limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/surah/info",
    summary="Get Surah General Info",
    description="Returns general information about a specific Surah, such as its name, names info, virtues, goals, and revelation order."
)
def get_surah_info_api(request: SurahRequest):
    try:
        from tafsir.tools.surah import get_surah_info
        result = get_surah_info(request.surah)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/surah/stats",
    summary="Get Surah Statistics",
    description="Returns detailed statistics for a specific Surah (word count, letter count, longest word, most frequent word, etc.)."
)
def get_surah_stats_api(request: SurahRequest):
    try:
        from tafsir.tools.stats import get_surah_statistics_summary
        result = get_surah_statistics_summary(request.surah)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/word/analysis",
    summary="Analyze Word",
    description="Analyzes a specific word in an ayah, showing its grammatical analysis (i'rab), morphology (sarf), vocabulary meaning, root, and frequency."
)
def get_word_analysis_api(request: WordRequest):
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if request.ayah > SURAH_AYAH_COUNTS.get(request.surah, 286):
            raise HTTPException(status_code=400, detail="رقم الآية خارج حدود السورة")
        
        from tafsir.tools.word import get_word_analysis
        result = get_word_analysis(request.surah, request.ayah, request.word_no, request.aspects)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/root/occurrences",
    summary="Find Root Occurrences",
    description="Finds all occurrences of a specific root in the Holy Quran (e.g., 'رحم', 'كتب'), listing surah, ayah, word number, and frequency."
)
def find_root_occurrences_api(request: RootOccurrencesRequest):
    try:
        from tafsir.tools.word import search_by_root
        result = search_by_root(request.root, limit=request.limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/root/stats",
    summary="Get Root Statistics",
    description="Returns aggregate statistics for a specific linguistic root (total occurrences, number of unique surahs/ayahs, and distinct morphological forms)."
)
def get_root_stats_api(request: RootStatsRequest):
    try:
        from tafsir.tools.word import get_root_statistics
        result = get_root_statistics(request.root)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/root/definition",
    summary="Get Root Definition in Classical Lexicons",
    description="Searches for the meaning of a linguistic root in classical Arabic lexicons: Lisan al-Arab, Maqayis al-Lugha, and Mufradat al-Raghib."
)
def get_root_definition_api(request: RootDefinitionRequest):
    try:
        from tafsir.tools.lexicon import get_root_definition
        result = get_root_definition(request.root)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/qeraat",
    summary="Compare Qeraat Variants",
    description="Compares different authentic Quranic readings (Qeraat) and variant pronunciations for a specific ayah or word."
)
def compare_qeraat_api(request: QeraatRequest):
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if request.ayah > SURAH_AYAH_COUNTS.get(request.surah, 286):
            raise HTTPException(status_code=400, detail="رقم الآية خارج حدود السورة")
        
        from tafsir.tools.qeraat import compare_qeraat
        result = compare_qeraat(request.surah, request.ayah, request.word_no)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/nuzool",
    summary="Get Ayah Nuzool Context",
    description="Returns the recorded context or cause of revelation (Asbab al-Nuzool) for a specific ayah, if documented in reliable sources."
)
def get_nuzool_api(request: NuzoolRequest):
    try:
        from tafsir.models import SURAH_AYAH_COUNTS
        if request.ayah > SURAH_AYAH_COUNTS.get(request.surah, 286):
            raise HTTPException(status_code=400, detail="رقم الآية خارج حدود السورة")
        
        from tafsir.tools.ayah import get_ayah_nuzool
        result = get_ayah_nuzool(request.surah, request.ayah)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/quran/overview",
    summary="Get Quran General Overview",
    description="Returns aggregate statistics and a general overview of the entire Quran (number of surahs, ayahs, unique roots, Makki/Madani surahs, pages)."
)
def get_quran_overview_api():
    try:
        from tafsir.tools.stats import get_quran_statistics
        result = get_quran_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/quran/fawaed",
    summary="Get Page Fawaed",
    description="Returns analytical, spiritual, or linguistic benefits (Fawaed) and insights recorded in 'Al-Mukhtasar' for a specific page of the Quran."
)
def get_page_fawaed_api(request: PageRequest):
    try:
        from tafsir.tools.stats import get_page_fawaed
        result = get_page_fawaed(request.page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/search/tafsir",
    summary="Search Tafsir Content",
    description="Searches for matching text snippets inside a specific tafsir source (e.g., saadi, katheer, qurtubi) with optional surah filters."
)
def search_tafsir_api(request: TafsirSearchRequest):
    try:
        from tafsir.tools.search import search_tafsir
        result = search_tafsir(request.query, source=request.source, surah_filter=request.surah_filter, limit=request.limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/debug",
    summary="Debug DB Status",
    description="Returns the disk status of all three tafsir databases on Render.",
    include_in_schema=False
)
def debug_db_status():
    import sqlite3
    from pathlib import Path
    from tafsir.data_loader import get_db_path, get_jalalayn_db_path, get_extended_db_path

    info = {}

    # quran.db
    try:
        p = Path(os.path.expanduser("~/.cache/tafsir-mcp/quran.db"))
        info["quran_db"] = {
            "path": str(p),
            "exists": p.exists(),
            "size_mb": round(p.stat().st_size / 1024 / 1024, 1) if p.exists() else 0
        }
        if p.exists():
            conn = sqlite3.connect(str(p))
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            info["quran_db"]["tables"] = tables
            conn.close()
    except Exception as e:
        info["quran_db"] = {"error": str(e)}

    # jalalayn.db
    try:
        p2 = Path(os.path.expanduser("~/.cache/tafsir-mcp/jalalayn.db"))
        info["jalalayn_db"] = {
            "path": str(p2),
            "exists": p2.exists(),
            "size_mb": round(p2.stat().st_size / 1024 / 1024, 1) if p2.exists() else 0
        }
    except Exception as e:
        info["jalalayn_db"] = {"error": str(e)}

    # extended_tafsir.db
    try:
        p3 = Path(os.path.expanduser("~/.cache/tafsir-mcp/extended_tafsir.db"))
        info["extended_db"] = {
            "path": str(p3),
            "exists": p3.exists(),
            "size_mb": round(p3.stat().st_size / 1024 / 1024, 1) if p3.exists() else 0
        }
        if p3.exists():
            conn3 = sqlite3.connect(str(p3))
            count = conn3.execute("SELECT COUNT(*) FROM tafsir_content").fetchone()[0]
            sources = [r[0] for r in conn3.execute("SELECT DISTINCT source FROM tafsir_content ORDER BY source").fetchall()]
            info["extended_db"]["row_count"] = count
            info["extended_db"]["sources"] = sources
            conn3.close()
    except Exception as e:
        info["extended_db"] = {"error": str(e)}

    # disk usage
    try:
        cache_dir = Path(os.path.expanduser("~/.cache/tafsir-mcp"))
        total_size = sum(f.stat().st_size for f in cache_dir.glob("*.db") if f.is_file())
        info["total_cache_size_mb"] = round(total_size / 1024 / 1024, 1)
    except Exception:
        pass

    return info

@app.get(
    "/sources",
    summary="List All Tafsir Sources",
    description="Returns a list of all 35 tafsir sources available in the system."
)
def list_sources():
    from tafsir.models import TafsirSource, TAFSIR_ATTRIBUTIONS
    sources = []
    quran_db_sources = {"tabary","katheer","baghawy","saadi","moyassar","mukhtasar_ar","mukhtasar_en","mukhtasar_bn"}
    jalalayn_sources = {"jalalayn"}
    for src in TafsirSource:
        if src.value in quran_db_sources:
            db = "quran.db"
        elif src.value in jalalayn_sources:
            db = "jalalayn.db"
        else:
            db = "extended_tafsir.db"
        sources.append({
            "key": src.value,
            "attribution": TAFSIR_ATTRIBUTIONS.get(src, ""),
            "database": db
        })
    return {"total": len(sources), "sources": sources}

# دمج تطبيق MCP داخل FastAPI بدعم Streamable HTTP الحديث
# المسار "/" - وسيرث FastMCP مسار /mcp داخلياً
# ملاحظة: مسارات FastAPI (@app.get/@app.post) لها أولوية على Mount في Starlette
if mcp_http is not None:
    try:
        app.mount("/", mcp_http)
        print("✅ تم دمج تطبيق MCP Streamable HTTP بنجاح عند المسار /mcp")
    except Exception as e:
        print(f"⚠️ فشل تركيب تطبيق MCP HTTP: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Running dual-protocol server on port {port}...")
    print(f"- ChatGPT REST API: http://127.0.0.1:{port}/extract")
    print(f"- MCP Endpoint:     http://127.0.0.1:{port}/mcp")
    uvicorn.run(app, host="0.0.0.0", port=port)

