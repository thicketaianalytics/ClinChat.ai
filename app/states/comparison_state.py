import reflex as rx
import logging
import polars as pl
from typing import cast
from app.models.trial import TrialDetail
from app.utils.polars_db import prepare_for_comparison
from app.utils.polars_db import export_df_to_csv
import datetime


class ComparisonState(rx.State):
    """The state for the trial comparison page."""

    selected_nct_ids: list[str] = []
    comparison_data: list[TrialDetail] = []
    is_loading: bool = False

    @rx.event(background=True)
    async def load_comparison_data(self):
        """Fetch full trial details for the selected NCT IDs."""
        if not self.selected_nct_ids:
            async with self:
                self.comparison_data = []
            return
        async with self:
            self.is_loading = True
            self.comparison_data = []
        try:
            df = prepare_for_comparison(self.selected_nct_ids)
            if df is not None and (not df.is_empty()):
                data = df.to_dicts()
                async with self:
                    self.comparison_data = [cast(TrialDetail, trial) for trial in data]
            else:
                async with self:
                    yield rx.toast.error("Could not load comparison data.")
        except Exception as e:
            logging.exception(f"Error loading comparison data: {e}")
            async with self:
                yield rx.toast.error("An error occurred while loading trial data.")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def handle_add_trial_submit(self, form_data: dict):
        """Handle the form submission for adding a new trial."""
        nct_id = form_data.get("nct_id", "").strip()
        if not nct_id:
            return rx.toast.warning("NCT ID cannot be empty.")
        return ComparisonState.add_trial_to_comparison(nct_id)

    @rx.event
    def add_trial_to_comparison(self, nct_id: str):
        """Add a trial to the comparison list."""
        if not nct_id.strip():
            return rx.toast.warning("NCT ID cannot be empty.")
        if len(self.selected_nct_ids) >= 5:
            return rx.toast.warning("You can compare a maximum of 5 trials.")
        if nct_id not in self.selected_nct_ids:
            self.selected_nct_ids.append(nct_id)
            return ComparisonState.load_comparison_data
        else:
            return rx.toast.info(f"Trial {nct_id} is already in the comparison list.")

    @rx.event
    def remove_trial_from_comparison(self, nct_id: str):
        """Remove a trial from the comparison list."""
        self.selected_nct_ids.remove(nct_id)
        self.comparison_data = [
            t for t in self.comparison_data if t["nct_id"] != nct_id
        ]

    @rx.event
    def clear_comparison(self):
        """Clear all selected trials from the comparison."""
        self.selected_nct_ids = []
        self.comparison_data = []

    @rx.event
    def set_selected_nct_ids(self, nct_ids: list[str]):
        """Set the selected NCT IDs for comparison (used when navigating from My Trials)."""
        self.selected_nct_ids = nct_ids[:5]
        return ComparisonState.load_comparison_data

    @rx.event(background=True)
    async def export_comparison_csv(self):
        """Export the comparison table to a CSV file."""
        if not self.comparison_data:
            async with self:
                yield rx.toast.error("No data to export.")
            return
        try:
            df = pl.DataFrame(self.comparison_data)
            csv_bytes = export_df_to_csv(df)
            if csv_bytes:
                filename = f"clinchat_comparison_{datetime.date.today()}.csv"
                async with self:
                    yield rx.download(data=csv_bytes, filename=filename)
            else:
                async with self:
                    yield rx.toast.error("Failed to generate CSV file.")
        except Exception as e:
            logging.exception(f"Error exporting comparison data: {e}")
            async with self:
                yield rx.toast.error("An error occurred during export.")