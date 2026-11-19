from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AnalysisRequest(BaseModel):
    dataset_id: str
    config: Optional[Dict[str, Any]] = None
    # какие группы искать, None - все
    groups: Optional[List[str]] = None


class SuggestRequest(BaseModel):
    dataset_id: str
