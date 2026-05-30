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



def _get_local_data_path(filename: str) -> Path:
    """الحصول على مسار ملف البيانات المحلي بدعم كلا الهيكلين (src/ أو Root)."""
    # 1. هيكل Root (الزيتونة الحالي)
    p1 = Path(__file__).parent.parent / "data" / filename
    if p1.exists():
        return p1
    # 2. هيكل src/ الاحتياطي (Tafsir MCP)
    p2 = Path(__file__).parent.parent.parent / "data" / filename
    if p2.exists():
        return p2
    return p1  # الافتراضي هو Root


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

    local = _get_local_data_path(DB_FILENAME)
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

    local = _get_local_data_path("jalalayn.db")
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


# ─── قواعد البيانات الموسعة (86 تفسيراً — 4 أجزاء مقسّمة) ───

EXTENDED_SHARD_FILES = [
    "extended_tafsir_s1.db",
    "extended_tafsir_s2.db",
    "extended_tafsir_s3.db",
    "extended_tafsir_s4.db",
]


def _download_shard_from_hf(shard_filename: str, target: Path) -> None:
    """تحميل ملف shard واحد من Hugging Face."""
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
        f"📥 Downloading {shard_filename} from Hugging Face...",
        file=sys.stderr,
    )

    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=shard_filename,
        repo_type="dataset",
        token=token,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded_path, target)

    size_mb = round(target.stat().st_size / 1024 / 1024, 1)
    print(f"✅ {shard_filename} saved ({size_mb} MB) → {target}", file=sys.stderr)


def get_extended_shard_path(shard_filename: str) -> Path:
    """احصل على مسار ملف shard معيّن مع تحميل تلقائي عند الحاجة.

    أولوية البحث:
    1. data/<shard> المحلي (المشروع / الإنتاج بعد البناء)
    2. ~/.cache/tafsir-mcp/<shard> (وضع الإنتاج الاحتياطي)
    """
    local = _get_local_data_path(shard_filename)
    if local.exists():
        return local

    cache_dir = Path.home() / ".cache" / "tafsir-mcp"
    cache_db = cache_dir / shard_filename

    if not cache_db.exists():
        try:
            _download_shard_from_hf(shard_filename, cache_db)
        except Exception as e:
            print(
                f"⚠️ فشل تحميل {shard_filename}: {e}\n"
                f"بعض التفاسير لن تكون متاحة.",
                file=sys.stderr,
            )
            return cache_db

    return cache_db


def get_extended_db_path() -> Path:
    """(توافق عكسي) يعيد مسار أول shard كبديل.

    ⚠️ مهمل: استخدم get_extended_shard_path() بدلاً منه.
    """
    return get_extended_shard_path(EXTENDED_SHARD_FILES[0])


# ─── قاعدة بيانات المعاجم اللغوية (لسان العرب، مقاييس اللغة، مفردات الأصفهاني) ───

LEXICONS_DB_FILENAME = "lexicons.db"


def _download_lexicons_from_hf(target: Path) -> None:
    """تحميل lexicons.db من Hugging Face عند أول تشغيل سحابي."""
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
        f"📥 Downloading Lexicons database from Hugging Face — first run only...",
        file=sys.stderr,
    )

    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=LEXICONS_DB_FILENAME,
        repo_type="dataset",
        token=token,
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded_path, target)

    print(f"✅ Lexicons database saved to {target}", file=sys.stderr)


def get_lexicon_db_path() -> Path:
    """احصل على مسار lexicons.db مع تحميل تلقائي عند الحاجة.

    أولوية البحث:
    1. متغير البيئة LEXICONS_DB_PATH
    2. data/lexicons.db المحلي (المشروع)
    3. ~/.cache/tafsir-mcp/lexicons.db (وضع الإنتاج، يُحمَّل من HF)
    """
    if env_path := os.environ.get("LEXICONS_DB_PATH"):
        path = Path(env_path)
        if path.exists():
            return path

    local = _get_local_data_path(LEXICONS_DB_FILENAME)
    if local.exists():
        return local

    cache_dir = Path.home() / ".cache" / "tafsir-mcp"
    cache_db = cache_dir / LEXICONS_DB_FILENAME

    if not cache_db.exists():
        try:
            _download_lexicons_from_hf(cache_db)
        except Exception as e:
            print(
                f"⚠️ فشل تحميل قاعدة بيانات المعاجم: {e}\n"
                f"المعاجم لن تكون متاحة.",
                file=sys.stderr,
            )
            return cache_db

    return cache_db


