# -*- coding: utf-8 -*-
"""
تحميل قواعد بيانات المصحف والتفسير والمعاجم بالكامل أثناء مرحلة البناء (Build Phase)
--------------------------------------------------------------------------------
يضمن هذا الملف تحميل القواعد سحابياً وتخزينها في مجلد data/ محلياً،
مما يمنع أي تحميل ديناميكي عند التشغيل، ويقضي على مشكلة نفاد الذاكرة (OOM) أو مسح الكاش.

v2.0: يستخدم 4 ملفات shard بدلاً من ملف extended_tafsir.db واحد (1 GB → 4 × 260 MB)
"""

import os
import shutil
import sys
from pathlib import Path

# إعداد ترميز الحروف لـ UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# مستودع هجينغ فيس والملفات المطلوبة
DB_REPO_ID = "asranko40/tafsir-mcp-data"
DB_FILES = {
    "quran.db": "quran.db",
    "jalalayn.db": "jalalayn.db",
    # 4 shards بدلاً من ملف extended_tafsir.db واحد
    "extended_tafsir_s1.db": "extended_tafsir_s1.db",
    "extended_tafsir_s2.db": "extended_tafsir_s2.db",
    "extended_tafsir_s3.db": "extended_tafsir_s3.db",
    "extended_tafsir_s4.db": "extended_tafsir_s4.db",
    "lexicons.db": "lexicons.db"
}

def main():
    print("🚀 Starting pre-download of all databases during build phase...")
    
    # تحديد مسار مجلد data المحلي
    current_dir = Path(__file__).parent.parent
    data_dir = current_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Target data directory: {data_dir.resolve()}")
    
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("❌ Error: huggingface_hub is not installed! Make sure to install requirements first.")
        sys.exit(1)
        
    token = os.environ.get("HF_TOKEN")
    if token:
        print("🔑 HF_TOKEN found in environment. Authenticated request enabled.")
    else:
        print("ℹ️ No HF_TOKEN found. Proceeding with public anonymous download.")

    for key, filename in DB_FILES.items():
        target_path = data_dir / filename
        if target_path.exists() and target_path.stat().st_size > 1000000: # 1MB
            print(f"✅ {filename} already exists and looks valid ({round(target_path.stat().st_size / 1024 / 1024, 1)} MB). Skipping download.")
            continue
            
        print(f"📥 Downloading {filename} from Hugging Face repository {DB_REPO_ID}...")
        sys.stdout.flush()
        
        try:
            downloaded_path = hf_hub_download(
                repo_id=DB_REPO_ID,
                filename=filename,
                repo_type="dataset",
                token=token
            )
            
            # نسخ الملف إلى مجلد data/
            shutil.copy2(downloaded_path, target_path)
            size_mb = round(target_path.stat().st_size / 1024 / 1024, 1)
            print(f"✅ Successfully downloaded and saved {filename} ({size_mb} MB) to local data directory.")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            sys.exit(1)

    # تنظيف ملف extended_tafsir.db القديم إن وُجد (لتوفير المساحة)
    old_extended = data_dir / "extended_tafsir.db"
    if old_extended.exists():
        print(f"🧹 Removing old extended_tafsir.db ({round(old_extended.stat().st_size / 1024 / 1024, 1)} MB) — replaced by 4 shards.")
        old_extended.unlink()
            
    print(f"\n🎉 All {len(DB_FILES)} databases successfully downloaded and packaged for production deployment!")

if __name__ == "__main__":
    main()
