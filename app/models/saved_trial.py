from typing import TypedDict, Optional
import datetime


class SavedTrial(TypedDict):
    nct_id: str
    brief_title: str
    overall_status: str
    phase: Optional[str]
    enrollment: Optional[int]
    start_date: Optional[str]
    completion_date: Optional[str]
    saved_date: str
    tags: list[str]
    notes: str
    last_updated: str