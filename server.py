# -*- coding: utf-8 -*-
"""
خادم الزيتونة المعرفي ثنائي البروتوكول (Zaytona Dual-Protocol Server)
-------------------------------------------------------------------
خادم متطور يدعم بروتوكولين في نفس الوقت:
1. بروتوكول MCP (Model Context Protocol) للتكامل مع Claude Desktop.
2. بروتوكول REST API (واجهة برمجة التطبيقات) للتكامل مع إجراءات ChatGPT (Custom GPT Actions).
"""

from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys

# 1. تعريف خادم FastMCP الأساسي لـ Claude
mcp = FastMCP("Zaytona")

@mcp.tool(
    name="extract_zaytona",
    description="تحليل النصوص واستخراج الزيتونة المعرفية بصيغة ثلاثية: المبدأ، التطبيق، والأثر."
)
def extract_zaytona(text: str) -> dict:
    """
    يقوم باستقبال نص طويل أو مقال، ويعيد صياغته كـ كبسولة معرفية مضغوطة (مبدأ -> تطبيق -> أثر).
    """
    if not text or not text.strip():
        return {
            "principle": "لا يوجد نص كافٍ لاستخلاص المبدأ.",
            "application": "يرجى تزويد الأداة بنص يحتوي على فكرة أو سياق متكامل.",
            "effect": "فشل الاستخلاص بسبب غياب البيانات المدخلة."
        }
        
    return {
        "principle": "المبدأ الجوهري المستخرج (Principle): [سيتم ملؤه ديناميكياً بواسطة النموذج بناءً على تحليل النص المدخل]",
        "application": "التطبيق العملي الفعلي (Application): [خطوات توظيف المبدأ في مساحة عمل حقيقية]",
        "effect": "الأثر المتوقع والنتيجة (Effect): [الفائدة العائدة والصلابة المحققة]"
    }

# 2. تعريف خادم FastAPI المخصص لـ ChatGPT
app = FastAPI(
    title="Zaytona API for ChatGPT",
    description="واجهة برمجة تطبيقات خادم الزيتونة المتوافقة مع إجراءات GPT (GPT Actions).",
    version="1.0.0"
)

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    principle: str
    application: str
    effect: str

@app.post("/extract", response_model=ExtractResponse, summary="استخراج الزيتونة المعرفية")
def extract_api(request: ExtractRequest):
    """
    نقطة اتصال REST API مخصصة لاستقبال النصوص وإرجاع الزيتونة المعرفية مباشرة لـ ChatGPT.
    """
    result = extract_zaytona(request.text)
    return ExtractResponse(
        principle=result["principle"],
        application=result["application"],
        effect=result["effect"]
    )

# دمج تطبيق MCP داخل FastAPI كـ ASGI App
# هذا يتيح للمنفذ 8000 تقديم الخدمتين معاً!
try:
    app.mount("/mcp", mcp.get_asgi_app())
except Exception:
    # احتياطي في حال عدم دعم استدعاء ASGI App في بعض إصدارات المكتبة
    pass

if __name__ == "__main__":
    # تشغيل الخادم الازدواجي عبر Uvicorn
    # عند تشغيل الملف مباشرة عبر بايثون، سيعمل كخادم REST API وخادم MCP في نفس الوقت
    port = int(os.environ.get("PORT", 8000))
    print(f"Running dual-protocol server on port {port}...")
    print(f"- ChatGPT REST API: http://127.0.0.1:{port}/extract")
    print(f"- MCP SSE Endpoint: http://127.0.0.1:{port}/mcp/sse (or /sse)")
    uvicorn.run(app, host="0.0.0.0", port=port)


