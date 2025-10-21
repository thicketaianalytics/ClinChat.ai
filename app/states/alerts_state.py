import reflex as rx
import uuid
import datetime
from typing import Optional, cast
import logging
from app.models.watchlist import Watchlist, WatchlistCriteria, WatchlistMatch
from app.models.trial import Trial
from app.states.auth_state import AuthState
from app.utils.db import get_db_connection, return_db_connection
from app.utils.polars_db import export_df_to_csv
import polars as pl

_watchlists_db: dict[str, dict[str, Watchlist]] = {}


class AlertsState(rx.State):
    watchlists: list[Watchlist] = []
    is_loading: bool = False
    show_create_dialog: bool = False
    selected_watchlist: Optional[Watchlist] = None
    matched_trials: list[Trial] = []
    is_checking: bool = False

    async def _get_user_email(self) -> str | None:
        auth_state = await self.get_state(AuthState)
        if auth_state.user:
            return auth_state.user.get("email")
        return None

    async def _get_user_watchlists(self) -> dict[str, Watchlist] | None:
        user_email = await self._get_user_email()
        if not user_email:
            return None
        if user_email not in _watchlists_db:
            _watchlists_db[user_email] = {}
        return _watchlists_db[user_email]

    @rx.event(background=True)
    async def load_watchlists(self):
        async with self:
            self.is_loading = True
        user_watchlists = await self._get_user_watchlists()
        if user_watchlists is not None:
            watchlists = sorted(
                list(user_watchlists.values()),
                key=lambda w: w["created_date"],
                reverse=True,
            )
            async with self:
                self.watchlists = watchlists
        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def create_watchlist(self, form_data: dict):
        user_watchlists = await self._get_user_watchlists()
        if user_watchlists is None:
            async with self:
                yield rx.toast.error("You must be logged in.")
            return
        name = form_data.get("name", "").strip()
        if not name:
            async with self:
                yield rx.toast.warning("Watchlist name is required.")
            return
        criteria = WatchlistCriteria(
            condition=form_data.get("condition"),
            intervention=form_data.get("intervention"),
            sponsor=form_data.get("sponsor"),
            phase=form_data.get("phase"),
            status=form_data.get("status"),
            country=form_data.get("country"),
        )
        if not any(criteria.values()):
            async with self:
                yield rx.toast.warning("At least one criterion is required.")
            return
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        watchlist_id = str(uuid.uuid4())
        new_watchlist = Watchlist(
            watchlist_id=watchlist_id,
            name=name,
            description=form_data.get("description", ""),
            criteria=criteria,
            created_date=now,
            last_checked=None,
            is_active=True,
            matches=[],
        )
        user_watchlists[watchlist_id] = new_watchlist
        async with self:
            self.watchlists.insert(0, new_watchlist)
            self.show_create_dialog = False
            yield rx.toast.success(f"Watchlist '{name}' created!")

    @rx.event
    def set_show_create_dialog(self, show: bool):
        self.show_create_dialog = show

    @rx.event(background=True)
    async def delete_watchlist(self, watchlist_id: str):
        user_watchlists = await self._get_user_watchlists()
        if user_watchlists and watchlist_id in user_watchlists:
            del user_watchlists[watchlist_id]
            async with self:
                self.watchlists = [
                    w for w in self.watchlists if w["watchlist_id"] != watchlist_id
                ]
                yield rx.toast.info("Watchlist deleted.")

    @rx.event(background=True)
    async def toggle_watchlist(self, watchlist_id: str):
        user_watchlists = await self._get_user_watchlists()
        if user_watchlists and watchlist_id in user_watchlists:
            watchlist = user_watchlists[watchlist_id]
            watchlist["is_active"] = not watchlist["is_active"]
            status = "activated" if watchlist["is_active"] else "deactivated"
            async with self:
                self.watchlists = [w for w in self.watchlists]
                yield rx.toast.success(f"Watchlist {status}.")

    @rx.event(background=True)
    async def check_watchlist(self, watchlist_id: str):
        async with self:
            self.is_checking = True
        user_watchlists = await self._get_user_watchlists()
        if not user_watchlists or watchlist_id not in user_watchlists:
            async with self:
                self.is_checking = False
                yield rx.toast.error("Watchlist not found.")
            return
        watchlist = user_watchlists[watchlist_id]
        criteria = watchlist["criteria"]
        where_clauses = []
        params = {}
        if criteria.get("condition"):
            where_clauses.append(
                "s.nct_id IN (SELECT nct_id FROM ctgov.conditions WHERE name ILIKE %(condition)s)"
            )
            params["condition"] = f"%{criteria['condition']}%"
        if criteria.get("intervention"):
            where_clauses.append(
                "s.nct_id IN (SELECT nct_id FROM ctgov.interventions WHERE name ILIKE %(intervention)s)"
            )
            params["intervention"] = f"%{criteria['intervention']}%"
        if criteria.get("sponsor"):
            where_clauses.append(
                "s.nct_id IN (SELECT nct_id FROM ctgov.sponsors WHERE name ILIKE %(sponsor)s)"
            )
            params["sponsor"] = f"%{criteria['sponsor']}%"
        if criteria.get("status"):
            where_clauses.append("s.overall_status = %(status)s")
            params["status"] = criteria["status"]
        if criteria.get("phase"):
            where_clauses.append("s.phase = %(phase)s")
            params["phase"] = criteria["phase"]
        if criteria.get("country"):
            where_clauses.append(
                "s.nct_id IN (SELECT nct_id FROM ctgov.facilities WHERE country ILIKE %(country)s)"
            )
            params["country"] = f"%{criteria['country']}%"
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=0"
        query = f"SELECT nct_id, brief_title, overall_status, phase, enrollment, start_date, completion_date, study_type, \n                    (SELECT COUNT(*) FROM ctgov.facilities WHERE nct_id = s.nct_id) as location_count, \n                    (SELECT COUNT(*) FROM ctgov.interventions WHERE nct_id = s.nct_id) as intervention_count \n                    FROM ctgov.studies s WHERE {where_sql} ORDER BY s.start_date DESC NULLS LAST LIMIT 100"
        conn = None
        new_matches = []
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    current_nct_ids = {m["nct_id"] for m in watchlist["matches"]}
                    for row in results:
                        nct_id = row[0]
                        if nct_id not in current_nct_ids:
                            new_matches.append(
                                WatchlistMatch(
                                    nct_id=nct_id,
                                    matched_date=now,
                                    match_reason="New trial found",
                                )
                            )
        except Exception as e:
            logging.exception(f"Error checking watchlist: {e}")
            async with self:
                yield rx.toast.error("An error occurred while checking.")
        finally:
            if conn:
                return_db_connection(conn)
            async with self:
                if new_matches:
                    watchlist["matches"].extend(new_matches)
                    watchlist["last_checked"] = datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat()
                    self.watchlists = list(user_watchlists.values())
                    yield rx.toast.success(
                        f"Found {len(new_matches)} new matching trials for '{watchlist['name']}'!"
                    )
                else:
                    yield rx.toast.info(
                        f"No new matches found for '{watchlist['name']}'."
                    )
                self.is_checking = False