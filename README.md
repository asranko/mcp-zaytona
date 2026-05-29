# خادم الزيتونة المعرفي (Zaytona MCP Server) 🫒

خادم متوافق مع بروتوكول سياق النماذج (Model Context Protocol - MCP) ومبني باستخدام بايثون وإطار العمل الحديث `FastMCP`. يقدم الخادم أداة تفاعلية تقوم بضغط المقالات والنصوص الطويلة واستخلاص **"الزيتونة المعرفية"** في ثلاثة أبعاد صارمة:
$$\text{الزيتونة} = \text{مبدأ (Principle)} \rightarrow \text{تطبيق (Application)} \rightarrow \text{أثر (Effect)}$$

---

## 📂 هيكل المشروع (Project Structure)

```text
mcp-zaytona/
├── server.py           # الكود المصدري للخادم وأدوات الاستخراج
├── requirements.txt    # الاعتماديات البرمجية اللازمة
├── render.yaml         # ملف التكوين التلقائي للنشر على Render
└── README.md           # دليل التشغيل والاستخدام (هذا الملف)
```

---

## 💻 التشغيل المحلي (Local Running)

### 1. إعداد البيئة الافتراضية وتثبيت المكتبات
قم بفتح الطرفية (Terminal) في مجلد المشروع ونفذ الأوامر التالية:

```bash
# إنشاء بيئة افتراضية لبايثون
python -m venv .venv

# تفعيل البيئة الافتراضية (على نظام Windows)
.venv\Scripts\activate

# تثبيت الاعتماديات المطلوبة
pip install -r requirements.txt
```

### 2. التشغيل والربط المحلي مع Claude Desktop (STDIO)
لتشغيل الخادم محلياً وربطه مع تطبيق Claude Desktop، ستحتاج إلى تعديل ملف إعدادات كلود الافتراضي:
* مسار الملف على Windows: `%APPDATA%\Claude\claude_desktop_config.json`

أضف الإعداد التالي في قائمة `mcpServers`:

```json
{
  "mcpServers": {
    "zaytona-mcp-local": {
      "command": "python",
      "args": [
        "C:/Users/moasran/Desktop/mcp octups/mcp-zaytona/server.py"
      ]
    }
  }
}
```
*ملاحظة: تأكد من كتابة المسار المطلق الصحيح لملف `server.py` واستبدال الخطوط المائلة الخلفية بـ `/`.*

---

## 🌐 النشر على منصة Render المجانية (Deployment on Render Free)

يدعم خادم الزيتونة النشر كخدمة ويب تعتمد على بروتوكول **الأحداث المرسلة من الخادم (SSE - Server-Sent Events)**، وهي الطريقة المثالية لتشغيله عبر الإنترنت وتكامله مع تطبيقات مثل Open WebUI أو مشاركته مع الآخرين.

### خطوات النشر التلقائي:

1. **الرفع إلى GitHub:**
   أطلق مستودعاً جديداً على حسابك في GitHub، وارفع محتويات مجلد `mcp-zaytona` إليه.

2. **التسجيل والنشر على Render:**
   * اذهب إلى موقع [Render](https://render.com).
   * قم بإنشاء حساب أو تسجيل الدخول عبر GitHub.
   * اضغط على **New** ثم اختر **Web Service**.
   * اربط مستودع GitHub الخاص بالمشروع.
    * سيقوم Render تلقائياً باكتشاف ملف `render.yaml` وسيتعرف على إعدادات التشغيل والبناء دون تدخل منك:
     - **أمر البناء (Build Command):** `pip install -r requirements.txt`
     - **أمر البدء (Start Command):** `python server.py`
   * اضغط على **Deploy**.

بعد اكتمال عملية البناء خلال دقائق، ستحصل على رابط الخدمة العام، وسيكون بالشكل التالي:
`https://zaytona-mcp.onrender.com`

---

## 🔌 التوصيل والربط مع المنصات المختلفة (Platform Integration Guide)

يقدم خادم الزيتونة دعماً ثنائياً متطوراً للتكامل مع أهم منصات الذكاء الاصطناعي:

### أولاً: التوصيل مع Claude Desktop (بروتوكول MCP SSE)
اربط الخادم المنشور سحابياً مع تطبيق كلود لسطح المكتب عن طريق إضافة الإعداد التالي لملف التكوين الخاص بك (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "zaytona-mcp-remote": {
      "sse": {
        "url": "https://zaytona-mcp.onrender.com/mcp/sse"
      }
    }
  }
}
```

---

### ثانياً: التوصيل مع ChatGPT (Custom GPT Actions)
يمكنك ربط الخادم كأداة ذكاء اصطناعي مخصصة (Action) في ChatGPT بسهولة بالغة وبأحد خيارين:

#### 💡 الطريقة الأسهل (الربط التلقائي عبر الرابط):
1. في صفحة تعديل الـ **Custom GPT** الخاص بك في ChatGPT، اذهب إلى قسم **Configure** ثم اضغط على **Create new action**.
2. ستجد خياراً يسمى **Import from URL**.
3. انسخ هذا الرابط والصقه هناك ثم اضغط **Import**:
   🔗 `https://zaytona-mcp.onrender.com/openapi.json`
4. سيقوم ChatGPT تلقائياً بقراءة المواصفات والاتصال بالسيرفر السحابي وتجهيز الأداة فوراً!

#### 🛠️ الطريقة البديلة (النسخ واللصق اليدوي لـ Schema):
إذا فضّلت لصق المواصفات يدوياً، قم بنسخ كود الـ JSON التالي وضعه في صندوق **Schema**:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Zaytona API for ChatGPT",
    "version": "1.0.0",
    "description": "واجهة برمجة تطبيقات خادم الزيتونة المتوافقة مع إجراءات GPT (GPT Actions)."
  },
  "servers": [
    {
      "url": "https://zaytona-mcp.onrender.com",
      "description": "خادم الزيتونة المعرفي السحابي (Render)"
    }
  ],
  "paths": {
    "/extract": {
      "post": {
        "summary": "استخراج الزيتونة المعرفية",
        "description": "نقطة اتصال REST API مخصصة لاستقبال النصوص وإرجاع الزيتونة المعرفية مباشرة لـ ChatGPT.",
        "operationId": "extract_api_extract_post",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "text": {
                    "type": "string",
                    "title": "Text",
                    "description": "النص المراد تحليل واستخلاص الزيتونة المعرفية منه."
                  }
                },
                "required": ["text"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "principle": {
                      "type": "string",
                      "title": "Principle"
                    },
                    "application": {
                      "type": "string",
                      "title": "Application"
                    },
                    "effect": {
                      "type": "string",
                      "title": "Effect"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## ⚠️ تنبيهات هامة بخصوص الحساب المجاني (Render Free Tier Notes)

> [!WARNING]
> خوادم الويب على منصة Render المجانية تدخل في **وضع الخمول (Spin Down/Sleep)** تلقائياً بعد **15 دقيقة** من عدم تلقي أي طلبات أو حركة مرور (Inactivity).

* **ماذا يحدث عند الخمول؟**
  عندما يرسل كلود أو ChatGPT طلباً بعد فترة خمول، سيستغرق الخادم ما يقارب **50 إلى 60 ثانية** للاستيقاظ وإعادة تشغيل الخدمة مجدداً. هذا سلوك طبيعي للمنصة المجانية ولا يعني وجود خطأ في البرمجة.
* **كيف تتفادى هذا؟**
  لتفادي خمول الخادم وجعله مستيقظاً بشكل دائم، يمكنك استخدام خدمة مجانية مثل [UptimeRobot](https://uptimerobot.com) لترسل طلباً (Ping) خفيفاً إلى رابط الخادم الرئيسي (`https://zaytona-mcp.onrender.com/`) كل 10 دقائق.

