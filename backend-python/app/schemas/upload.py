from pydantic import BaseModel


class UploadResponse(BaseModel):
    status: str
    message: str
    dataset_id: str
    file_name: str
    file_type: str