import asyncio
import logging
import time
from pathlib import Path


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"

RETENTION_SECONDS = 3 * 24 * 60 * 60
CLEANUP_INTERVAL = 60 * 60

logger = logging.getLogger(__name__)


def cleanup_old_uploads():
    if not UPLOAD_DIR.exists():
        return

    current_time = time.time()

    for file_path in UPLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue

        try:
            file_age = current_time - file_path.stat().st_mtime

            if file_age >= RETENTION_SECONDS:
                file_path.unlink()
                logger.info("Deleted old upload: %s", file_path.name)

        except OSError:
            logger.exception("Could not delete file: %s", file_path)


async def cleanup_loop():
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        await asyncio.to_thread(cleanup_old_uploads)