from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException

from app.schemas.upload import UploadResponse
from app.services.dataset_registry import register_dataset


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


async def process_uploaded_file(file: UploadFile) -> UploadResponse:
    allowed_extensions = [".csv", ".json", ".xlsx"]

    file_name = file.filename or ""
    extension = Path(file_name).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only CSV, JSON and XLSX files are allowed"
        )

    dataset_id = str(uuid4())
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / f"{dataset_id}{extension}"

    try:
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
    finally:
        await file.close()

    register_dataset(
        dataset_id=dataset_id,
        file_path=file_path,
        file_name=file_name,
        file_type=extension[1:]
    )

    return UploadResponse(
        status="success",
        message="File uploaded successfully",
        dataset_id=dataset_id,
        file_name=file_name,
        file_type=extension[1:]
    )