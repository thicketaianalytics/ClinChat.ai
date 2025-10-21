import reflex as rx
import logging
from typing import cast
from app.utils.ai_helper import ai_client
from app.states.trial_detail_state import TrialDetailState
from app.states.comparison_state import ComparisonState


class AIState(rx.State):
    """State for managing AI-powered features."""

    ai_summaries: dict[str, str] = {}
    is_generating_summary: set[str] = set()
    summary_error: str = ""
    comparison_insights: str = ""
    is_generating_insights: bool = False

    @rx.var
    def current_provider(self) -> str:
        provider = ai_client.get_provider()
        return provider.capitalize() if provider else "N/A"

    @rx.event(background=True)
    async def generate_trial_summary(self, nct_id: str):
        async with self:
            if nct_id in self.is_generating_summary:
                return
            self.is_generating_summary.add(nct_id)
            yield rx.toast.info(f"Generating AI summary for {nct_id}...")
        try:
            async with self:
                trial_detail_state = await self.get_state(TrialDetailState)
                trial = trial_detail_state.trial
            if not trial or trial.get("nct_id") != nct_id:
                async with self:
                    yield rx.toast.error("Trial data not available for summary.")
                return
            prompt = f"Please provide a concise, expert-level summary for the clinical trial with NCT ID {trial.get('nct_id')}. \n            The trial is titled '{trial.get('brief_title')}' and is currently in status '{trial.get('overall_status')}' and phase '{trial.get('phase')}'.\n\n            Here is the brief summary: {trial.get('brief_summary')}\n\n            Here are the eligibility criteria: {trial.get('eligibility_criteria')}\n\n            Based on this information, generate a summary covering the following points in bullet format:\n            - **Key Objective**: What is the main goal of this study?\n            - **Primary Population**: Who are the main participants (based on inclusion/exclusion criteria)?\n            - **Key Endpoints**: What are the primary outcomes being measured?\n            - **Potential Significance**: What is the potential impact or significance of this trial in its field? \n            \n            Keep the language professional and targeted at a clinical research audience."
            summary_text = ai_client.generate_content(
                prompt, cache_key=f"summary_{nct_id}"
            )
            async with self:
                self.ai_summaries[nct_id] = summary_text
                if "Error:" not in summary_text:
                    yield rx.toast.success("AI Summary generated!")
                else:
                    yield rx.toast.error(summary_text)
        except Exception as e:
            logging.exception("Error generating AI trial summary.")
            async with self:
                self.summary_error = "Failed to generate summary."
                yield rx.toast.error(self.summary_error)
        finally:
            async with self:
                self.is_generating_summary.remove(nct_id)

    @rx.event(background=True)
    async def generate_comparison_insights(self):
        async with self:
            if self.is_generating_insights:
                return
            self.is_generating_insights = True
            self.comparison_insights = ""
            yield rx.toast.info("Generating AI comparison insights...")
        try:
            async with self:
                comparison_state = await self.get_state(ComparisonState)
            if not comparison_state.comparison_data:
                async with self:
                    yield rx.toast.warning("No trials to compare.")
                return
            trials_summary = []
            for trial in comparison_state.comparison_data:
                trials_summary.append(
                    f"- NCT ID: {trial['nct_id']}, Title: {trial['brief_title']}, Status: {trial['overall_status']}, Phase: {trial['phase']}, Enrollment: {trial['enrollment']}"
                )
            prompt = f"As a clinical research analyst, provide a comparative analysis of the following clinical trials:\n\n            {chr(10).join(trials_summary)}\n\n            Your analysis should be a narrative that includes:\n            1.  **Key Differences**: Highlight the most significant differences in trial design (e.g., phase, status, enrollment size).\n            2.  **Potential Similarities**: Identify any underlying similarities in objectives or scope that might not be immediately obvious.\n            3.  **Strategic Insight**: Based on the data, offer a brief strategic insight. For example, which trial appears to be higher risk but higher reward? Which is a later-stage validation? \n\n            Present this as a concise report for a strategy meeting. Use bold headings for each section."
            insights_text = ai_client.generate_content(
                prompt, cache_key=f"compare_{comparison_state.selected_nct_ids}"
            )
            async with self:
                self.comparison_insights = insights_text
                if "Error:" not in insights_text:
                    yield rx.toast.success("AI Insights generated!")
                else:
                    yield rx.toast.error(insights_text)
        except Exception as e:
            logging.exception("Error generating AI comparison insights.")
            async with self:
                yield rx.toast.error("Failed to generate comparison insights.")
        finally:
            async with self:
                self.is_generating_insights = False