import reflex as rx
import logging
from app.utils.db import get_db_connection, return_db_connection


class DashboardState(rx.State):
    """The state for the dashboard page."""

    is_loading: bool = True
    total_trials: int = 0
    active_trials: int = 0
    completed_trials: int = 0
    phase_1_trials: int = 0
    phase_2_trials: int = 0
    phase_3_trials: int = 0
    phase_4_trials: int = 0
    recent_trials: list[dict[str, str]] = []

    @rx.event(background=True)
    async def load_dashboard_data(self):
        """Load dashboard metrics from the database."""
        async with self:
            self.is_loading = True
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM ctgov.studies")
                    total = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM ctgov.studies WHERE overall_status = 'RECRUITING'"
                    )
                    active = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM ctgov.studies WHERE overall_status = 'COMPLETED'"
                    )
                    completed = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM ctgov.studies WHERE phase = 'PHASE1'"
                    )
                    phase_1 = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM ctgov.studies WHERE phase = 'PHASE2'"
                    )
                    phase_2 = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM ctgov.studies WHERE phase = 'PHASE3'"
                    )
                    phase_3 = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM ctgov.studies WHERE phase = 'PHASE4'"
                    )
                    phase_4 = cur.fetchone()[0]
                    cur.execute(
                        "SELECT nct_id, brief_title, overall_status, phase, enrollment, start_date FROM ctgov.studies ORDER BY study_first_posted_date DESC LIMIT 8"
                    )
                    recent = [
                        dict(zip([desc[0] for desc in cur.description], row))
                        for row in cur.fetchall()
                    ]
                    async with self:
                        self.total_trials = total
                        self.active_trials = active
                        self.completed_trials = completed
                        self.phase_1_trials = phase_1
                        self.phase_2_trials = phase_2
                        self.phase_3_trials = phase_3
                        self.phase_4_trials = phase_4
                        self.recent_trials = recent
                    yield
            else:
                logging.error("Failed to get database connection.")
        except Exception as e:
            logging.exception(f"Error loading dashboard data: {e}")
        finally:
            if conn:
                return_db_connection(conn)
            async with self:
                self.is_loading = False