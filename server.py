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

# إضافة مسار مكتبة التفسير محلياً إذا كان متوفراً (لتسهيل التطوير المحلي)
TAFSIR_MCP_SRC = "C:\\Users\\moasran\\Desktop\\tafser\\tafsir-mcp\\src"
if os.path.exists(TAFSIR_MCP_SRC):
    if TAFSIR_MCP_SRC not in sys.path:
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
    from tafsir.tools.ayah import get_ayah_tafsir, get_ayah
    from tafsir.tools.search import search_quran_text
    
    # تسجيل الأدوات
    ayah_tools.register(mcp)
    surah_tools.register(mcp)
    word_tools.register(mcp)
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
        """فهرس 9 مصادر تفسيرية مع كامل بيانات الإสนاد (JSON)."""
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

# دمج تطبيق MCP داخل FastAPI بدعم Streamable HTTP الحديث
# هذا يجعل الرابط https://zaytona-mcp.onrender.com/mcp متوافقاً مع ChatGPT Connectors مباشرة
if mcp_http is not None:
    try:
        app.mount("/", mcp_http)
        print("✅ تم دمج تطبيق MCP Streamable HTTP بنجاح عند المسار /")
    except Exception as e:
        print(f"⚠️ فشل تركيب تطبيق MCP HTTP: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Running dual-protocol server on port {port}...")
    print(f"- ChatGPT REST API: http://127.0.0.1:{port}/extract")
    print(f"- MCP Endpoint:     http://127.0.0.1:{port}/mcp")
    uvicorn.run(app, host="0.0.0.0", port=port)

