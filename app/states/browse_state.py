import reflex as rx
import logging
from typing import Any, cast
from app.models.trial import Trial, TrialDetail
from app.utils.db import get_db_connection, return_db_connection


class BrowseState(rx.State):
    trials: list[Trial] = []
    total_trials: int = 0
    is_table_loading: bool = True
    is_detail_loading: bool = False
    _filter_options_loaded: bool = False
    current_page: int = 1
    items_per_page: int = 15
    search_terms: dict[str, str] = {
        "nct_id": "",
        "condition": "",
        "intervention": "",
        "sponsor": "",
        "status": "",
        "phase": "",
        "study_type": "",
    }
    filter_options: dict[str, list[str]] = {
        "statuses": [],
        "phases": [],
        "study_types": [],
    }
    selected_trial: TrialDetail = cast(TrialDetail, {})
    similar_trials: list[Trial] = []
    bookmark_loading: dict[str, bool] = {}

    @rx.var
    def total_pages(self) -> int:
        if self.total_trials == 0:
            return 1
        return -(-self.total_trials // self.items_per_page)

    @rx.event(background=True)
    async def load_browse_page_data(self):
        """Load filter options (if not already loaded) and trial data."""
        async with self:
            self.is_table_loading = True
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                logging.error("Database connection failed.")
                async with self:
                    self.is_table_loading = False
                return
            if not self._filter_options_loaded:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DISTINCT overall_status FROM ctgov.studies WHERE overall_status IS NOT NULL ORDER BY overall_status"
                    )
                    statuses = [row[0] for row in cur.fetchall()]
                    cur.execute(
                        "SELECT DISTINCT phase FROM ctgov.studies WHERE phase IS NOT NULL ORDER BY phase"
                    )
                    phases = [row[0] for row in cur.fetchall()]
                    cur.execute(
                        "SELECT DISTINCT study_type FROM ctgov.studies WHERE study_type IS NOT NULL ORDER BY study_type"
                    )
                    study_types = [row[0] for row in cur.fetchall()]
                    async with self:
                        self.filter_options["statuses"] = statuses
                        self.filter_options["phases"] = phases
                        self.filter_options["study_types"] = study_types
                        self._filter_options_loaded = True
            yield BrowseState.fetch_trials
        except Exception as e:
            logging.exception(f"Error loading browse page data: {e}")
            async with self:
                self.is_table_loading = False
        finally:
            if conn:
                return_db_connection(conn)

    @rx.event(background=True)
    async def fetch_trials(self):
        """Fetch trials based on current search terms and pagination."""
        async with self:
            self.is_table_loading = True
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    where_clauses = []
                    params = {}
                    if self.search_terms.get("nct_id"):
                        where_clauses.append("s.nct_id ILIKE %(nct_id)s")
                        params["nct_id"] = f"%{self.search_terms['nct_id']}%"
                    if self.search_terms.get("condition"):
                        where_clauses.append(
                            "s.nct_id IN (SELECT nct_id FROM ctgov.conditions WHERE name ILIKE %(condition)s)"
                        )
                        params["condition"] = f"%{self.search_terms['condition']}%"
                    if self.search_terms.get("intervention"):
                        where_clauses.append(
                            "s.nct_id IN (SELECT nct_id FROM ctgov.interventions WHERE name ILIKE %(intervention)s)"
                        )
                        params["intervention"] = (
                            f"%{self.search_terms['intervention']}%"
                        )
                    if self.search_terms.get("sponsor"):
                        where_clauses.append(
                            "s.nct_id IN (SELECT nct_id FROM ctgov.sponsors WHERE name ILIKE %(sponsor)s)"
                        )
                        params["sponsor"] = f"%{self.search_terms['sponsor']}%"
                    if self.search_terms.get("status"):
                        where_clauses.append("s.overall_status = %(status)s")
                        params["status"] = self.search_terms["status"]
                    if self.search_terms.get("phase"):
                        where_clauses.append("s.phase = %(phase)s")
                        params["phase"] = self.search_terms["phase"]
                    if self.search_terms.get("study_type"):
                        where_clauses.append("s.study_type = %(study_type)s")
                        params["study_type"] = self.search_terms["study_type"]
                    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
                    count_query = (
                        f"SELECT COUNT(*) FROM ctgov.studies s WHERE {where_sql}"
                    )
                    cur.execute(count_query, params)
                    total = cur.fetchone()[0]
                    offset = (self.current_page - 1) * self.items_per_page
                    params.update({"limit": self.items_per_page, "offset": offset})
                    data_query = f"\n                    WITH FirstMesh AS (\n                        SELECT nct_id, mesh_term, ROW_NUMBER() OVER(PARTITION BY nct_id ORDER BY id) as rn\n                        FROM ctgov.browse_conditions\n                    )\n                    SELECT \n                        s.nct_id, s.brief_title, s.overall_status, s.phase, s.enrollment, s.start_date, s.completion_date, s.study_type,\n                        (SELECT COUNT(*) FROM ctgov.facilities WHERE nct_id = s.nct_id) as location_count,\n                        (SELECT COUNT(*) FROM ctgov.interventions WHERE nct_id = s.nct_id) as intervention_count,\n                        fm.mesh_term as primary_therapeutic_area\n                    FROM ctgov.studies s\n                    LEFT JOIN FirstMesh fm ON s.nct_id = fm.nct_id AND fm.rn = 1\n                    WHERE {where_sql}\n                    ORDER BY s.start_date DESC NULLS LAST \n                    LIMIT %(limit)s OFFSET %(offset)s\n                    "
                    cur.execute(data_query, params)
                    trials_data = [
                        dict(zip([desc[0] for desc in cur.description], row))
                        for row in cur.fetchall()
                    ]
                    async with self:
                        self.total_trials = total
                        self.trials = trials_data
        except Exception as e:
            logging.exception(f"Error fetching trials: {e}")
        finally:
            if conn:
                return_db_connection(conn)
            async with self:
                self.is_table_loading = False

    @rx.event
    def set_search_term(self, name: str, value: str):
        self.search_terms[name] = value

    @rx.event
    def handle_search(self, form_data: dict[str, Any]):
        self.current_page = 1
        return BrowseState.fetch_trials

    @rx.event
    def reset_filters(self):
        self.search_terms = {k: "" for k in self.search_terms}
        self.current_page = 1
        return BrowseState.fetch_trials

    @rx.event
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            return BrowseState.fetch_trials

    @rx.event
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            return BrowseState.fetch_trials

    @rx.event
    def go_to_trial_detail(self, nct_id: str):
        return rx.redirect(f"/trial/{nct_id}")

    @rx.event(background=True)
    async def bookmark_trial(self, nct_id: str):
        async with self:
            self.bookmark_loading[nct_id] = True
        try:
            from app.states.saved_trials_state import SavedTrialsState

            saved_trials_state = None
            async with self:
                saved_trials_state = await self.get_state(SavedTrialsState)
            if saved_trials_state:
                async for event in saved_trials_state.save_trial(nct_id):
                    yield event
        except Exception as e:
            logging.exception(f"Failed to bookmark trial {nct_id}: {e}")
            async with self:
                yield rx.toast.error("Failed to save trial.")
        finally:
            async with self:
                if nct_id in self.bookmark_loading:
                    del self.bookmark_loading[nct_id]