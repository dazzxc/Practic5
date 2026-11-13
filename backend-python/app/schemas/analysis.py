from pydantic import BaseModel
from typing import Optional, Dict, Any

class AnalysisRequest(BaseModel):
    dataset_id: str
    config: Optional[Dict[str, Any]] = None