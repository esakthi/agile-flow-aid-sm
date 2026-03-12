from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DashboardMetric(BaseModel):
    title: str
    value: Any

class VisualisationSpec(BaseModel):
    type: str
    title: str
    data_source: str

class Alert(BaseModel):
    severity: str
    message: str

class Drilldowns(BaseModel):
    epic_to_story: bool = True
    story_to_commit: bool = True
    commit_to_build: bool = True
    build_to_acceptance: bool = True

class DashboardResponse(BaseModel):
    role: str
    summary: str
    metrics: Dict[str, Any]
    visualisations: List[VisualisationSpec]
    drilldowns: Drilldowns
    alerts: List[Alert]

class ChatQuery(BaseModel):
    query: str
    role: str
    deep_search: bool = False

class ChatResponse(BaseModel):
    response: str
    role: str
    voice_summary: Optional[str] = None
    grounding_metadata: Optional[Dict[str, Any]] = None
