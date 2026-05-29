"""Database loader with automatic download from Hugging Face Datasets."""
import hashlib
import os
import shutil
import sys
from pathlib import Path

DB_REPO_ID = "asranko40/tafsir-mcp-data"
DB_FILENAME = "quran.db"
DB_SHA256 = "10e61f615ab5e6a3440e8ecc8ba1dc2273d12cd9048752760fe53a44d191cc27"
DB_SIZE_MB = 214


def _verify_sha256(path: Path) -> None:
    """تحقّق من سلامة الملف عبر SHA256."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    actual = h.hexdigest()
    if actual != DB_SHA256:
        path.unlink(missing_ok=True)
        raise RuntimeError(
            f"تعارض في SHA256 لقاعدة البيانات المحمّلة!\n"
            f"  متوقع: {DB_SHA256}\n"
            f"  فعلي:  {actual}\n"
            f"تم حذف الملف الفاسد. أعد المحاولة أو أبلغ عن المشكلة."
        )


def _download_from_hf(target: Path) -> None:
    """تحميل DB من Hugging Face عبر مكتبة huggingface_hub.

    تستخدم certifi لإدارة SSL تلقائياً، وتدعم Resume.
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise RuntimeError(
            "مكتبة huggingface_hub غير متوفرة. "
            "ثبّتها عبر: pip install huggingface_hub"
        ) from e

    print(
        f"📥 Downloading Tafsir database ({DB_SIZE_MB} MB) "
        f"from Hugging Face — first run only...",
        file=sys.stderr,
    )

    downloaded_path = hf_hub_download(
        repo_id=DB_REPO_ID,
        filename=DB_FILENAME,
        repo_type="dataset",
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded_path, target)

    print(f"✅ Database saved to {target}", file=sys.stderr)


def get_db_path() -> Path:
    """احصل على مسار quran.db مع تحميل تلقائي عند الحاجة.

    أولوية البحث:
    1. متغير البيئة TAFSIR_DB_PATH (وضع التطوير)
    2. data/quran.db المحلي (المشروع)
    3. ~/.cache/tafsir-mcp/quran.db (وضع الإنتاج، يُحمَّل من HF)
    """
    if env_path := os.environ.get("TAFSIR_DB_PATH"):
        path = Path(env_path)
        if path.exists():
            return path

    local = Path(__file__).parent.parent.parent / "data" / DB_FILENAME
    if local.exists():
        return local

    cache_dir = Path.home() / ".cache" / "tafsir-mcp"
    cache_db = cache_dir / DB_FILENAME

    if not cache_db.exists():
        try:
            _download_from_hf(cache_db)
            _verify_sha256(cache_db)
        except Exception as e:
            raise RuntimeError(
                f"فشل تحميل قاعدة البيانات من {DB_REPO_ID}: {e}\n"
                f"يمكنك ضبط TAFSIR_DB_PATH لمسار quran.db محلي."
            ) from e

    return cache_db


def _download_jalalayn_from_hf(target: Path) -> None:
    """تحميل jalalayn.db من Hugging Face عند أول تشغيل سحابي."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise RuntimeError(
            "مكتبة huggingface_hub غير متوفرة. "
            "ثبّتها عبر: pip install huggingface_hub"
        ) from e

    repo_id = os.environ.get("HF_REPO_ID", DB_REPO_ID)
    token = os.environ.get("HF_TOKEN")

    print(
        f"📥 Downloading Jalalayn database from Hugging Face — first run only...",
        file=sys.stderr,
    )

    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename="jalalayn.db",
        repo_type="dataset",
        token=token,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded_path, target)

    print(f"✅ Jalalayn database saved to {target}", file=sys.stderr)


def get_jalalayn_db_path() -> Path:
    """احصل على مسار jalalayn.db مع تحميل تلقائي عند الحاجة.

    أولوية البحث:
    1. متغير البيئة JALALAYN_DB_PATH
    2. data/jalalayn.db المحلي (المشروع)
    3. ~/.cache/tafsir-mcp/jalalayn.db (وضع الإنتاج، يُحمَّل من HF)
    """
    if env_path := os.environ.get("JALALAYN_DB_PATH"):
        path = Path(env_path)
        if path.exists():
            return path

    local = Path(__file__).parent.parent.parent / "data" / "jalalayn.db"
    if local.exists():
        return local

    cache_dir = Path.home() / ".cache" / "tafsir-mcp"
    cache_db = cache_dir / "jalalayn.db"

    if not cache_db.exists():
        try:
            _download_jalalayn_from_hf(cache_db)
        except Exception as e:
            print(
                f"⚠️ فشل تحميل قاعدة بيانات الجلالين: {e}\n"
                f"تفسير الجلالين لن يكون متاحاً.",
                file=sys.stderr,
            )
            return cache_db

    return cache_db


# ─── قاعدة البيانات الموسعة (32 تفسيراً إضافياً) ───

EXTENDED_DB_FILENAME = "extended_tafsir.db"
EXTENDED_DB_SIZE_MB = 385


def _download_extended_from_hf(target: Path) -> None:
    """تحميل extended_tafsir.db من Hugging Face عند أول تشغيل سحابي."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        raise RuntimeError(
            "مكتبة huggingface_hub غير متوفرة. "
            "ثبّتها عبر: pip install huggingface_hub"
        ) from e

    repo_id = os.environ.get("HF_REPO_ID", DB_REPO_ID)
    token = os.environ.get("HF_TOKEN")

    print(
        f"📥 Downloading Extended Tafsir database ({EXTENDED_DB_SIZE_MB} MB) "
        f"from Hugging Face — first run only...",
        file=sys.stderr,
    )

    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=EXTENDED_DB_FILENAME,
        repo_type="dataset",
        token=token,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded_path, target)

    print(f"✅ Extended database saved to {target}", file=sys.stderr)


def get_extended_db_path() -> Path:
    """احصل على مسار extended_tafsir.db مع تحميل تلقائي عند الحاجة.

    أولوية البحث:
    1. متغير البيئة EXTENDED_TAFSIR_DB_PATH
    2. data/extended_tafsir.db المحلي (المشروع)
    3. ~/.cache/tafsir-mcp/extended_tafsir.db (وضع الإنتاج، يُحمَّل من HF)
    """
    if env_path := os.environ.get("EXTENDED_TAFSIR_DB_PATH"):
        path = Path(env_path)
        if path.exists():
            return path

    local = Path(__file__).parent.parent.parent / "data" / EXTENDED_DB_FILENAME
    if local.exists():
        return local

    cache_dir = Path.home() / ".cache" / "tafsir-mcp"
    cache_db = cache_dir / EXTENDED_DB_FILENAME

    if not cache_db.exists():
        try:
            _download_extended_from_hf(cache_db)
        except Exception as e:
            print(
                f"⚠️ فشل تحميل قاعدة البيانات الموسعة: {e}\n"
                f"التفاسير الموسعة لن تكون متاحة.",
                file=sys.stderr,
            )
            return cache_db  # يعيد المسار حتى لو لم يوجد الملف

    return cache_db

