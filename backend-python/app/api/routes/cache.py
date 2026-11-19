from fastapi import APIRouter
from app.services.cache_service import clear_cache

router = APIRouter()

@router.delete("/cache")
def clear_scan_cache():
    deleted = clear_cache()
    return {
        "status": "success",
        "message": f"Кэш очищен. Удалено файлов: {deleted}"
    }