import reflex as rx
import logging
import datetime
from typing import Any
from app.states.trial_detail_state import TrialDetailState
from app.states.comparison_state import ComparisonState
from app.states.analytics_state import AnalyticsState
from app.states.saved_trials_state import SavedTrialsState
from app.utils.report_generator import (
    generate_trial_detail_pdf_from_state,
    generate_comparison_pdf_from_state,
    generate_excel_report_from_state,
)


class ReportState(rx.State):
    """Manages the generation of PDF and Excel reports."""

    is_generating_pdf: bool = False
    is_generating_excel: bool = False

    @rx.event(background=True)
    async def generate_trial_pdf(self):
        """Generates a PDF report for the current trial detail view."""
        try:
            async with self:
                self.is_generating_pdf = True
                yield rx.toast.info("Generating PDF report...")
                trial_detail_state = await self.get_state(TrialDetailState)
            if not trial_detail_state.trial:
                async with self:
                    yield rx.toast.error("No trial data to generate report.")
                    return
            pdf_bytes = generate_trial_detail_pdf_from_state(trial_detail_state)
            if pdf_bytes:
                filename = f"ClinChat_Trial_{trial_detail_state.trial['nct_id']}.pdf"
                async with self:
                    yield rx.download(data=pdf_bytes, filename=filename)
                    yield rx.toast.success("PDF report generated successfully!")
            else:
                async with self:
                    yield rx.toast.error("Failed to generate PDF report.")
        except Exception as e:
            logging.exception(f"Error generating trial detail PDF: {e}")
            async with self:
                yield rx.toast.error("An error occurred during PDF generation.")
        finally:
            async with self:
                self.is_generating_pdf = False

    @rx.event(background=True)
    async def generate_comparison_pdf(self):
        """Generates a PDF report for the current trial comparison."""
        try:
            async with self:
                self.is_generating_pdf = True
                yield rx.toast.info("Generating comparison PDF...")
                comparison_state = await self.get_state(ComparisonState)
            if not comparison_state.comparison_data:
                async with self:
                    yield rx.toast.error("No comparison data to generate report.")
                    return
            pdf_bytes = generate_comparison_pdf_from_state(comparison_state)
            if pdf_bytes:
                filename = f"ClinChat_Comparison_{datetime.date.today()}.pdf"
                async with self:
                    yield rx.download(data=pdf_bytes, filename=filename)
                    yield rx.toast.success("Comparison PDF generated!")
            else:
                async with self:
                    yield rx.toast.error("Failed to generate comparison PDF.")
        except Exception as e:
            logging.exception(f"Error generating comparison PDF: {e}")
            async with self:
                yield rx.toast.error("An error occurred during PDF generation.")
        finally:
            async with self:
                self.is_generating_pdf = False

    @rx.event(background=True)
    async def generate_saved_trials_excel(self):
        """Generates an Excel workbook for saved trials."""
        try:
            async with self:
                self.is_generating_excel = True
                yield rx.toast.info("Generating Excel workbook...")
                saved_trials_state = await self.get_state(SavedTrialsState)
            if not saved_trials_state.saved_trials:
                async with self:
                    yield rx.toast.error("No saved trials to export.")
                    return
            excel_bytes = generate_excel_report_from_state(saved_trials_state)
            if excel_bytes:
                filename = f"ClinChat_Saved_Trials_{datetime.date.today()}.xlsx"
                async with self:
                    yield rx.download(data=excel_bytes, filename=filename)
                    yield rx.toast.success("Excel report generated!")
            else:
                async with self:
                    yield rx.toast.error("Failed to generate Excel workbook.")
        except Exception as e:
            logging.exception(f"Error generating saved trials Excel: {e}")
            async with self:
                yield rx.toast.error("An error occurred during Excel generation.")
        finally:
            async with self:
                self.is_generating_excel = False