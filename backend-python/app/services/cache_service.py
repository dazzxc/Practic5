import json
import hashlib
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

# Папка, куда будем сохранять кэш
CACHE_DIR = Path(__file__).resolve().parents[2] / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_file_hash(file_path: Path) -> str:
    """Считает SHA256 хэш файла"""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def make_cache_key(file_hash: str, config: dict | None, groups: list | None) -> str:
    payload = {
        "file_hash": file_hash,
        "config": config or {},
        "groups": sorted(groups) if groups else None
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _get_cache_path(cache_key: str) -> Path:
    return CACHE_DIR / f"{cache_key}.json"


def get_cached_report(cache_key: str) -> Optional[dict]:
    cache_file = _get_cache_path(cache_key)
   
    if not cache_file.exists():
        return None
        
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        # если файл битый — просто игнорируем
        return None


def save_cached_report(cache_key: str, report_data: dict) -> None:
    cache_file = _get_cache_path(cache_key)
    
    # Добавляем мета-информацию
    data_to_save = {
        **report_data,
        "cached_at": datetime.now().isoformat(timespec="seconds")
    }
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)


def clear_cache() -> int:
    count = 0
    for file in CACHE_DIR.glob("*.json"):
        file.unlink()
        count += 1
    return count