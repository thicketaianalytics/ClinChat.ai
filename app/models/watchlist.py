from typing import TypedDict, Optional
import datetime


class WatchlistCriteria(TypedDict):
    condition: Optional[str]
    intervention: Optional[str]
    sponsor: Optional[str]
    phase: Optional[str]
    status: Optional[str]
    country: Optional[str]


class WatchlistMatch(TypedDict):
    nct_id: str
    matched_date: str
    match_reason: str


class Watchlist(TypedDict):
    watchlist_id: str
    name: str
    description: str
    criteria: WatchlistCriteria
    created_date: str
    last_checked: Optional[str]
    is_active: bool
    matches: list[WatchlistMatch]