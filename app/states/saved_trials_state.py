import reflex as rx
import logging
import datetime
from typing import cast
import polars as pl
from app.models.saved_trial import SavedTrial
from app.states.auth_state import AuthState
from app.utils.db import get_db_connection, return_db_connection
from app.utils.polars_db import export_df_to_csv

_saved_trials_db: dict[str, dict[str, SavedTrial]] = {}


class SavedTrialsState(rx.State):
    saved_trials: list[SavedTrial] = []
    is_loading: bool = False
    selected_nct_ids: list[str] = []
    filter_tag: str = "All"
    available_tags: list[str] = [
        "All",
        "High Priority",
        "Under Review",
        "Archived",
        "To Compare",
    ]

    @rx.var
    def filtered_trials(self) -> list[SavedTrial]:
        if self.filter_tag == "All":
            return self.saved_trials
        return [t for t in self.saved_trials if self.filter_tag in t["tags"]]

    @rx.var
    def available_tags_for_bulk_add(self) -> list[str]:
        return [tag for tag in self.available_tags if tag != "All"]

    async def _get_user_trials(self) -> dict[str, SavedTrial] | None:
        auth_state = await self.get_state(AuthState)
        user = auth_state.user
        if not user:
            return None
        if user["email"] not in _saved_trials_db:
            _saved_trials_db[user["email"]] = {}
        return _saved_trials_db[user["email"]]

    @rx.event(background=True)
    async def load_saved_trials(self):
        async with self:
            self.is_loading = True
        try:
            user_trials = await self._get_user_trials()
            if user_trials is not None:
                async with self:
                    self.saved_trials = sorted(
                        list(user_trials.values()),
                        key=lambda t: t["saved_date"],
                        reverse=True,
                    )
        except Exception as e:
            logging.exception(f"Error loading saved trials: {e}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def save_trial(self, nct_id: str):
        user_trials = await self._get_user_trials()
        if user_trials is None:
            async with self:
                yield rx.toast.error("You must be logged in to save trials.")
            return
        if nct_id in user_trials:
            async with self:
                yield rx.toast.info(f"Trial {nct_id} is already saved.")
            return
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT nct_id, brief_title, overall_status, phase, enrollment, start_date, completion_date FROM ctgov.studies WHERE nct_id = %s",
                        (nct_id,),
                    )
                    row = cur.fetchone()
                    if row:
                        trial_data = dict(zip([d[0] for d in cur.description], row))
                        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        saved_trial = SavedTrial(
                            **trial_data,
                            saved_date=now,
                            tags=[],
                            notes="",
                            last_updated=now,
                        )
                        user_trials[nct_id] = saved_trial
                        async with self:
                            self.saved_trials.insert(0, saved_trial)
                            yield rx.toast.success(f"Trial {nct_id} saved!")
                    else:
                        async with self:
                            yield rx.toast.error(f"Trial {nct_id} not found.")
        except Exception as e:
            logging.exception(f"Error saving trial {nct_id}: {e}")
            async with self:
                yield rx.toast.error("Failed to save trial.")
        finally:
            if conn:
                return_db_connection(conn)

    @rx.event
    async def remove_trial(self, nct_id: str):
        user_trials = await self._get_user_trials()
        if user_trials and nct_id in user_trials:
            del user_trials[nct_id]
            self.saved_trials = [t for t in self.saved_trials if t["nct_id"] != nct_id]
            self.selected_nct_ids = [i for i in self.selected_nct_ids if i != nct_id]
            return rx.toast.info(f"Trial {nct_id} removed.")

    @rx.event
    async def add_tag(self, nct_id: str, tag: str):
        user_trials = await self._get_user_trials()
        if user_trials and nct_id in user_trials:
            if tag not in user_trials[nct_id]["tags"]:
                user_trials[nct_id]["tags"].append(tag)
                user_trials[nct_id]["last_updated"] = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()
                self.saved_trials = list(user_trials.values())

    @rx.event
    async def remove_tag(self, nct_id: str, tag: str):
        user_trials = await self._get_user_trials()
        if user_trials and nct_id in user_trials:
            if tag in user_trials[nct_id]["tags"]:
                user_trials[nct_id]["tags"].remove(tag)
                user_trials[nct_id]["last_updated"] = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()
                self.saved_trials = list(user_trials.values())

    @rx.event
    async def update_notes(self, nct_id: str, notes: str):
        user_trials = await self._get_user_trials()
        if user_trials and nct_id in user_trials:
            user_trials[nct_id]["notes"] = notes
            user_trials[nct_id]["last_updated"] = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()
            self.saved_trials = list(user_trials.values())

    @rx.event
    def toggle_selection(self, nct_id: str):
        if nct_id in self.selected_nct_ids:
            self.selected_nct_ids.remove(nct_id)
        else:
            self.selected_nct_ids.append(nct_id)

    @rx.event
    async def bulk_remove(self):
        user_trials = await self._get_user_trials()
        if user_trials:
            removed_count = 0
            for nct_id in self.selected_nct_ids:
                if nct_id in user_trials:
                    del user_trials[nct_id]
                    removed_count += 1
            self.saved_trials = [
                t for t in self.saved_trials if t["nct_id"] not in self.selected_nct_ids
            ]
            self.selected_nct_ids = []
            return rx.toast.info(f"{removed_count} trials removed.")

    @rx.event
    async def bulk_add_tag(self, tag: str):
        user_trials = await self._get_user_trials()
        if user_trials:
            updated_count = 0
            for nct_id in self.selected_nct_ids:
                if nct_id in user_trials and tag not in user_trials[nct_id]["tags"]:
                    user_trials[nct_id]["tags"].append(tag)
                    updated_count += 1
            self.saved_trials = list(user_trials.values())
            self.selected_nct_ids = []
            return rx.toast.success(f"Tag '{tag}' added to {updated_count} trials.")

    @rx.event
    def set_filter_tag(self, tag: str):
        self.filter_tag = tag

    @rx.event
    def go_to_comparison(self):
        from app.states.comparison_state import ComparisonState

        if not self.selected_nct_ids:
            return rx.toast.warning("Select trials to compare first.")
        return (
            ComparisonState.set_selected_nct_ids(self.selected_nct_ids),
            rx.redirect("/compare"),
        )

    @rx.var
    async def is_trial_saved(self) -> dict[str, bool]:
        user_trials = await self._get_user_trials()
        if not user_trials:
            return {}
        return {nct_id: True for nct_id in user_trials}

    @rx.event(background=True)
    async def export_to_csv(self):
        user_trials = await self._get_user_trials()
        if not user_trials:
            async with self:
                yield rx.toast.error("No saved trials to export.")
            return
        df = pl.DataFrame(list(user_trials.values()))
        csv_bytes = export_df_to_csv(df)
        async with self:
            if csv_bytes:
                yield rx.download(
                    data=csv_bytes,
                    filename=f"clinchat_saved_trials_{datetime.date.today()}.csv",
                )
            else:
                yield rx.toast.error("Failed to export data.")