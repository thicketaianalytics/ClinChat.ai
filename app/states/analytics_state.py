import reflex as rx
import logging
from typing import Any
from app.utils.polars_db import (
    get_phase_distribution,
    get_status_distribution,
    get_enrollment_trends,
    get_geographic_distribution,
    get_top_sponsors,
    get_timeline_data,
    get_top_conditions,
    get_top_interventions,
    export_df_to_csv,
    get_us_state_distribution,
    get_trial_duration_distribution,
    get_design_patterns,
    get_trending_conditions,
)
import polars as pl
import datetime


class AnalyticsState(rx.State):
    is_loading: bool = True
    phase_distribution: list[dict] = []
    status_distribution: list[dict] = []
    enrollment_trends: list[dict] = []
    geographic_distribution: list[dict] = []
    sponsor_analysis: list[dict] = []
    timeline_data: list[dict] = []
    top_conditions: list[dict] = []
    top_interventions: list[dict] = []
    us_state_distribution: list[dict] = []
    trial_duration_distribution: list[dict] = []
    design_patterns: list[dict] = []
    trending_conditions: list[dict] = []
    active_tab: str = "overview"

    @rx.event(background=True)
    async def load_analytics_data(self):
        async with self:
            self.is_loading = True
        try:
            phase_df = get_phase_distribution()
            status_df = get_status_distribution()
            enrollment_df = get_enrollment_trends()
            geo_df = get_geographic_distribution()
            sponsor_df = get_top_sponsors()
            timeline_df = get_timeline_data()
            conditions_df = get_top_conditions()
            interventions_df = get_top_interventions()
            us_state_df = get_us_state_distribution()
            duration_df = get_trial_duration_distribution()
            design_df = get_design_patterns()
            trending_cond_df = get_trending_conditions()
            async with self:
                if phase_df is not None:
                    self.phase_distribution = phase_df.to_dicts()
                if status_df is not None:
                    self.status_distribution = status_df.to_dicts()
                if enrollment_df is not None:
                    self.enrollment_trends = enrollment_df.to_dicts()
                if geo_df is not None:
                    self.geographic_distribution = geo_df.to_dicts()
                if sponsor_df is not None:
                    self.sponsor_analysis = sponsor_df.to_dicts()
                if timeline_df is not None:
                    self.timeline_data = timeline_df.to_dicts()
                if conditions_df is not None:
                    self.top_conditions = conditions_df.to_dicts()
                if interventions_df is not None:
                    self.top_interventions = interventions_df.to_dicts()
                if us_state_df is not None:
                    self.us_state_distribution = us_state_df.to_dicts()
                if duration_df is not None:
                    self.trial_duration_distribution = duration_df.to_dicts()
                if design_df is not None:
                    self.design_patterns = design_df.to_dicts()
                if trending_cond_df is not None:
                    self.trending_conditions = trending_cond_df.to_dicts()
        except Exception as e:
            logging.exception(f"Error loading analytics data: {e}")
            async with self:
                yield rx.toast.error("Failed to load analytics data.")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_active_tab(self, tab_name: str):
        self.active_tab = tab_name

    @rx.event(background=True)
    async def export_analytics_report(self):
        try:
            df = pl.DataFrame(self.phase_distribution)
            csv_bytes = export_df_to_csv(df, filename="phase_distribution.csv")
            if csv_bytes:
                filename = f"clinchat_analytics_report_{datetime.date.today()}.csv"
                async with self:
                    yield rx.download(data=csv_bytes, filename=filename)
            else:
                async with self:
                    yield rx.toast.error("Failed to generate analytics report.")
        except Exception as e:
            logging.exception(f"Error exporting analytics: {e}")
            async with self:
                yield rx.toast.error("An error occurred during export.")