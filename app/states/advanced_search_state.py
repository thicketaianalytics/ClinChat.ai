import reflex as rx
import logging
import re
import datetime
from typing import TypedDict, cast
from app.states.auth_state import AuthState
from app.utils.db import get_db_connection, return_db_connection
from app.models.trial import Trial


class SearchQuery(TypedDict):
    natural_query: str
    structured_query: dict[str, str]
    timestamp: str


class SavedSearch(SearchQuery):
    name: str


_query_history_db: dict[str, list[SearchQuery]] = {}
_saved_searches_db: dict[str, list[SavedSearch]] = {}


class AdvancedSearchState(rx.State):
    natural_query: str = ""
    structured_query: dict[str, str] = {
        "condition": "",
        "intervention": "",
        "sponsor": "",
        "status": "",
        "phase": "",
        "min_enrollment": "",
        "max_enrollment": "",
        "start_date_from": "",
        "start_date_to": "",
    }
    search_results: list[Trial] = []
    total_results: int = 0
    is_searching: bool = False
    query_history: list[SearchQuery] = []
    saved_searches: list[SavedSearch] = []

    async def _get_user_email(self) -> str | None:
        auth_state = await self.get_state(AuthState)
        if auth_state.user:
            return auth_state.user.get("email")
        return None

    async def _load_user_data(self):
        user_email = await self._get_user_email()
        if user_email:
            self.query_history = _query_history_db.setdefault(user_email, [])
            self.saved_searches = _saved_searches_db.setdefault(user_email, [])

    @rx.event
    async def on_page_load(self):
        await self._load_user_data()

    def _parse_natural_query(self):
        query = self.natural_query.lower()
        parsed_terms = {
            "condition": "",
            "intervention": "",
            "sponsor": "",
            "status": "",
            "phase": "",
            "min_enrollment": "",
            "max_enrollment": "",
            "start_date_from": "",
            "start_date_to": "",
        }
        phase_mappings = {
            "early phase 1": "EARLY_PHASE1",
            "phase 1/2": "PHASE1/PHASE2",
            "phase 2/3": "PHASE2/PHASE3",
            "phase 1": "PHASE1",
            "phase 2": "PHASE2",
            "phase 3": "PHASE3",
            "phase 4": "PHASE4",
            "n/a": "NA",
        }
        for pattern, value in phase_mappings.items():
            if re.search("\\b" + pattern + "\\b", query):
                parsed_terms["phase"] = value
                break
        status_mappings = {
            "recruiting": "RECRUITING",
            "completed": "COMPLETED",
            "active": "ACTIVE",
            "terminated": "TERMINATED",
        }
        for term, value in status_mappings.items():
            if "\\b" + term + "\\b" in query:
                parsed_terms["status"] = value
                break
        condition_match = re.search(
            "(?:on|for)\\s+([a-z'\\s-]+?)(?=\\s+since|\\s+with|\\s+by|$)", query
        )
        if condition_match:
            parsed_terms["condition"] = condition_match.group(1).strip()
        sponsor_match = re.search(
            "(?:with|by|sponsor(?:ed by)?)\\s+([a-z\\s.-]+?)(?=\\s+as sponsor|\\s+since|$)",
            query,
        )
        if sponsor_match:
            parsed_terms["sponsor"] = sponsor_match.group(1).strip()
        since_match = re.search("since\\s+(\\d{4})", query)
        if since_match:
            parsed_terms["start_date_from"] = f"{since_match.group(1)}-01-01"
        self.structured_query = parsed_terms

    @rx.event
    def handle_natural_query_submit(self, form_data: dict):
        self.natural_query = form_data.get("natural_query", "").strip()
        self._parse_natural_query()
        return AdvancedSearchState.execute_search()

    @rx.event
    def handle_structured_query_submit(self, form_data: dict):
        self.structured_query.update(form_data)
        return AdvancedSearchState.execute_search()

    @rx.event(background=True)
    async def execute_search(self):
        async with self:
            self.is_searching = True
            self.search_results = []
        where_clauses = []
        params = {}
        for key, value in self.structured_query.items():
            if value:
                if key == "condition":
                    where_clauses.append(
                        "s.nct_id IN (SELECT nct_id FROM ctgov.conditions WHERE name ILIKE %(condition)s)"
                    )
                    params["condition"] = f"%{value}%"
                elif key == "intervention":
                    where_clauses.append(
                        "s.nct_id IN (SELECT nct_id FROM ctgov.interventions WHERE name ILIKE %(intervention)s)"
                    )
                    params["intervention"] = f"%{value}%"
                elif key == "sponsor":
                    where_clauses.append(
                        "s.nct_id IN (SELECT nct_id FROM ctgov.sponsors WHERE name ILIKE %(sponsor)s)"
                    )
                    params["sponsor"] = f"%{value}%"
                elif key == "status":
                    where_clauses.append("s.overall_status = %(status)s")
                    params["status"] = value
                elif key == "phase":
                    where_clauses.append("s.phase = %(phase)s")
                    params["phase"] = value
                elif key == "min_enrollment":
                    where_clauses.append("s.enrollment >= %(min_enrollment)s")
                    params["min_enrollment"] = int(value)
                elif key == "max_enrollment":
                    where_clauses.append("s.enrollment <= %(max_enrollment)s")
                    params["max_enrollment"] = int(value)
                elif key == "start_date_from":
                    where_clauses.append("s.start_date >= %(start_date_from)s")
                    params["start_date_from"] = value
                elif key == "start_date_to":
                    where_clauses.append("s.start_date <= %(start_date_to)s")
                    params["start_date_to"] = value
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"SELECT nct_id, brief_title, overall_status, phase, enrollment, start_date, completion_date, study_type, (SELECT COUNT(*) FROM ctgov.facilities WHERE nct_id = s.nct_id) as location_count, (SELECT COUNT(*) FROM ctgov.interventions WHERE nct_id = s.nct_id) as intervention_count FROM ctgov.studies s WHERE {where_sql} ORDER BY s.start_date DESC NULLS LAST LIMIT 50"
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    results = [
                        dict(zip([desc[0] for desc in cur.description], row))
                        for row in cur.fetchall()
                    ]
                    async with self:
                        self.search_results = [cast(Trial, r) for r in results]
                        self.total_results = len(results)
                        await self._add_to_history()
            else:
                async with self:
                    yield rx.toast.error("Database connection failed.")
        except Exception as e:
            logging.exception(f"Error executing search: {e}")
            async with self:
                yield rx.toast.error("An error occurred during search.")
        finally:
            if conn:
                return_db_connection(conn)
            async with self:
                self.is_searching = False

    async def _add_to_history(self):
        user_email = await self._get_user_email()
        if user_email:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            new_entry = SearchQuery(
                natural_query=self.natural_query,
                structured_query=self.structured_query,
                timestamp=now,
            )
            user_history = _query_history_db.setdefault(user_email, [])
            user_history.insert(0, new_entry)
            _query_history_db[user_email] = user_history[:10]
            self.query_history = _query_history_db[user_email]

    @rx.event
    def load_from_history(self, query: SearchQuery):
        self.natural_query = query["natural_query"]
        self.structured_query = query["structured_query"]
        return AdvancedSearchState.execute_search()

    @rx.event
    def save_current_search(self, search_name: str):
        if not search_name.strip():
            return rx.toast.warning("Search name cannot be empty.")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        new_saved_search = SavedSearch(
            name=search_name,
            natural_query=self.natural_query,
            structured_query=self.structured_query,
            timestamp=now,
        )
        user_email = self.user.get("email")
        if user_email:
            user_searches = _saved_searches_db.setdefault(user_email, [])
            user_searches.append(new_saved_search)
            self.saved_searches = user_searches
            return rx.toast.success(f"Search '{search_name}' saved.")

    @rx.event
    def load_saved_search(self, search: SavedSearch):
        self.natural_query = search["natural_query"]
        self.structured_query = search["structured_query"]
        return AdvancedSearchState.execute_search()

    @rx.event
    def delete_saved_search(self, search_name: str):
        user_email = self.user.get("email")
        if user_email:
            user_searches = _saved_searches_db.get(user_email, [])
            _saved_searches_db[user_email] = [
                s for s in user_searches if s["name"] != search_name
            ]
            self.saved_searches = _saved_searches_db[user_email]
            return rx.toast.info(f"Search '{search_name}' deleted.")