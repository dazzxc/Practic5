from fastapi import APIRouter, UploadFile, File
from app.schemas.upload import UploadResponse
from app.services.file_service import process_uploaded_file

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    return await process_uploaded_file(file)