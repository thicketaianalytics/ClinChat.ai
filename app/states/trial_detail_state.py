import reflex as rx
import logging
import re
from typing import cast, TypedDict
from app.models.trial import Trial, TrialDetail
from app.utils.db import get_db_connection, return_db_connection
from app.models.trial import DesignOutcome
from reflex_enterprise.components.map.types import LatLng, latlng
import datetime


class TimelineEntry(TypedDict):
    name: str
    start: str | None
    end: str | None


class ComplexityFactors(TypedDict):
    locations: int
    interventions: int
    outcomes: int
    sponsors: int
    design_groups: int


class TrialDetailState(rx.State):
    is_loading: bool = True
    trial: TrialDetail = cast(TrialDetail, {})
    similar_trials: list[Trial] = []
    sponsor_portfolio: list[Trial] = []
    map_center: LatLng = latlng(lat=0, lng=0)
    map_zoom: float = 2.0

    @rx.var
    def _nct_id_from_route(self) -> str:
        """Get the nct_id from the router params."""
        return self.router.page.params.get("nct_id", "")

    @rx.var
    def primary_outcomes(self) -> list[DesignOutcome]:
        """Return primary design outcomes."""
        outcomes = self.trial.get("design_outcomes", [])
        if not outcomes:
            return []
        return [o for o in outcomes if o.get("outcome_type") == "primary"]

    @rx.var
    def secondary_outcomes(self) -> list[DesignOutcome]:
        """Return secondary design outcomes."""
        outcomes = self.trial.get("design_outcomes", [])
        if not outcomes:
            return []
        return [o for o in outcomes if o.get("outcome_type") == "secondary"]

    def _parse_criteria(self, text: str | None) -> tuple[list[str], list[str], str]:
        if not text:
            return ([], [], "")
        inclusion_keywords = ("Inclusion Criteria:", "Key Inclusion Criteria:")
        exclusion_keywords = ("Exclusion Criteria:", "Key Exclusion Criteria:")
        note_keyword = "Note:"
        text = text.replace(
            "\\n",
            """
""",
        )
        parts = re.split(f"({'|'.join(exclusion_keywords)})", text, flags=re.IGNORECASE)
        inclusion_text = parts[0]
        exclusion_text = "".join(parts[1:]) if len(parts) > 1 else ""
        for keyword in inclusion_keywords:
            if keyword.lower() in inclusion_text.lower():
                inclusion_text = re.split(keyword, inclusion_text, flags=re.IGNORECASE)[
                    -1
                ]
                break
        note_parts = re.split(f"({note_keyword})", exclusion_text, flags=re.IGNORECASE)
        main_exclusion_text = note_parts[0]
        note = "".join(note_parts[1:]).strip() if len(note_parts) > 1 else ""
        for keyword in exclusion_keywords:
            if keyword.lower() in main_exclusion_text.lower():
                main_exclusion_text = re.split(
                    keyword, main_exclusion_text, flags=re.IGNORECASE
                )[-1]
                break
        inclusion_items = [
            item.strip() for item in inclusion_text.split("*") if item.strip()
        ]
        exclusion_items = [
            item.strip() for item in main_exclusion_text.split("*") if item.strip()
        ]
        return (inclusion_items, exclusion_items, note)

    @rx.var
    def inclusion_criteria(self) -> list[str]:
        criteria_text = self.trial.get("eligibility_criteria")
        return self._parse_criteria(criteria_text)[0]

    @rx.var
    def exclusion_criteria(self) -> list[str]:
        criteria_text = self.trial.get("eligibility_criteria")
        return self._parse_criteria(criteria_text)[1]

    @rx.var
    def eligibility_note(self) -> str:
        """Extract note section from eligibility criteria if present."""
        criteria = self.trial.get("eligibility_criteria", "")
        if not criteria:
            return ""
        note_lines = []
        capture = False
        for line in criteria.split("""
"""):
            line_stripped = line.strip()
            if line_stripped.lower().startswith("note:"):
                capture = True
            if capture and line_stripped:
                note_lines.append(line_stripped)
        if note_lines:
            note_lines[0] = note_lines[0][5:].strip()
            return " ".join(filter(None, note_lines))
        return ""

    @rx.var
    def complexity_factors(self) -> ComplexityFactors:
        if not self.trial:
            return {
                "locations": 0,
                "interventions": 0,
                "outcomes": 0,
                "sponsors": 0,
                "design_groups": 0,
            }
        return {
            "locations": len(self.trial.get("locations", [])),
            "interventions": len(self.trial.get("interventions", [])),
            "outcomes": len(self.trial.get("design_outcomes", [])),
            "sponsors": len(self.trial.get("sponsors", [])),
            "design_groups": len(self.trial.get("design_groups", [])),
        }

    @rx.var
    def complexity_score(self) -> int:
        factors = self.complexity_factors
        score = sum(factors.values())
        return score

    @rx.var
    def lead_sponsor(self) -> dict | None:
        sponsors = self.trial.get("sponsors", [])
        if not sponsors:
            return None
        for sponsor in sponsors:
            if sponsor.get("lead_or_collaborator") == "lead":
                return sponsor
        return None

    @rx.var
    def complexity_rating(self) -> str:
        score = self.complexity_score
        if score < 10:
            return "Low"
        if score < 25:
            return "Medium"
        if score < 50:
            return "High"
        return "Very High"

    @rx.var
    def trial_duration_days(self) -> int:
        if not self.trial.get("start_date") or not self.trial.get("completion_date"):
            return 0
        try:
            start = datetime.datetime.fromisoformat(self.trial["start_date"])
            end = datetime.datetime.fromisoformat(self.trial["completion_date"])
            return (end - start).days
        except (ValueError, TypeError) as e:
            logging.exception(f"Error calculating trial duration: {e}")
            return 0

    @rx.var
    def location_markers(self) -> list[dict]:
        markers = []
        if not self.trial.get("locations"):
            return []
        known_locations = {
            "United States": latlng(39.8, -98.6),
            "Canada": latlng(56.1, -106.3),
            "France": latlng(46.2, 2.2),
            "Germany": latlng(51.1, 10.4),
            "United Kingdom": latlng(55.4, -3.4),
        }
        locations = self.trial.get("locations", [])
        if not locations:
            return []
        for loc in locations:
            country = loc.get("country")
            if country in known_locations:
                base_latlng = known_locations[country]
                lat = base_latlng["lat"] + hash(loc.get("city", "")) % 100 / 100.0 - 0.5
                lng = (
                    base_latlng["lng"]
                    + hash(loc.get("facility", "")) % 100 / 100.0
                    - 0.5
                )
                markers.append(
                    {
                        "position": latlng(lat=lat, lng=lng),
                        "popup": f"<strong>{loc.get('facility', 'N/A')}</strong><br/>{loc.get('city', '')}, {country}<br/>Status: {loc.get('status', 'N/A')}",
                    }
                )
        return markers

    @rx.event(background=True)
    async def load_trial_details(self):
        async with self:
            self.is_loading = True
            self.trial = cast(TrialDetail, {})
            self.similar_trials = []
            self.sponsor_portfolio = []
        conn = None
        try:
            conn = get_db_connection()
            nct_id = self._nct_id_from_route
            if conn and nct_id:
                with conn.cursor() as cur:
                    study_query = """
                    SELECT 
                        s.nct_id, s.brief_title, s.official_title, s.overall_status, s.phase,
                        s.study_type, s.enrollment, s.start_date, s.completion_date,
                        bs.description as brief_summary,
                        dd.description as detailed_description,
                        e.criteria as eligibility_criteria
                    FROM ctgov.studies s
                    LEFT JOIN ctgov.brief_summaries bs ON s.nct_id = bs.nct_id
                    LEFT JOIN ctgov.detailed_descriptions dd ON s.nct_id = dd.nct_id
                    LEFT JOIN ctgov.eligibilities e ON s.nct_id = e.nct_id
                    WHERE s.nct_id = %s
                    """
                    cur.execute(study_query, (nct_id,))
                    row = cur.fetchone()
                    if not row:
                        async with self:
                            self.is_loading = False
                        return
                    trial_data = dict(zip([desc[0] for desc in cur.description], row))
                    cur.execute(
                        "SELECT name as facility, status, city, state, zip, country FROM ctgov.facilities WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["locations"] = [
                        dict(zip([d[0] for d in cur.description], r))
                        for r in cur.fetchall()
                    ]
                    cur.execute(
                        "SELECT intervention_type, name FROM ctgov.interventions WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["interventions"] = [
                        dict(zip([d[0] for d in cur.description], r))
                        for r in cur.fetchall()
                    ]
                    cur.execute(
                        "SELECT agency_class, lead_or_collaborator, name FROM ctgov.sponsors WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["sponsors"] = [
                        dict(zip([d[0] for d in cur.description], r))
                        for r in cur.fetchall()
                    ]
                    cur.execute(
                        "SELECT group_type, title, description FROM ctgov.design_groups WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["design_groups"] = [
                        dict(zip([d[0] for d in cur.description], r))
                        for r in cur.fetchall()
                    ]
                    cur.execute(
                        "SELECT outcome_type, measure, time_frame, description FROM ctgov.design_outcomes WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["design_outcomes"] = [
                        dict(zip([d[0] for d in cur.description], r))
                        for r in cur.fetchall()
                    ]
                    cur.execute(
                        "SELECT citation, reference_type FROM ctgov.study_references WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["references"] = [
                        dict(zip([d[0] for d in cur.description], r))
                        for r in cur.fetchall()
                    ]
                    cur.execute(
                        "SELECT mesh_term FROM ctgov.browse_conditions WHERE nct_id = %s",
                        (nct_id,),
                    )
                    trial_data["mesh_terms"] = [r[0] for r in cur.fetchall()]
                    cur.execute(
                        "SELECT name FROM ctgov.conditions WHERE nct_id = %s", (nct_id,)
                    )
                    trial_data["conditions"] = [r[0] for r in cur.fetchall()]
                    async with self:
                        self.trial = cast(TrialDetail, trial_data)
                        if self.trial.get("locations"):
                            first_country = self.trial["locations"][0].get("country")
                            country_centers = {
                                "United States": latlng(39.8, -98.6),
                                "Canada": latlng(56.1, -106.3),
                                "France": latlng(46.2, 2.2),
                                "Germany": latlng(51.1, 10.4),
                                "United Kingdom": latlng(55.4, -3.4),
                            }
                            self.map_center = country_centers.get(
                                first_country, latlng(0, 0)
                            )
                            self.map_zoom = (
                                4.0 if first_country in country_centers else 2.0
                            )
                    yield TrialDetailState.fetch_similar_trials(nct_id, self.trial)
                    yield TrialDetailState.fetch_sponsor_portfolio(self.trial)
        except Exception as e:
            logging.exception(f"Error fetching trial details: {e}")
        finally:
            if conn:
                return_db_connection(conn)
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def fetch_similar_trials(self, nct_id: str, trial_data: TrialDetail):
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name FROM ctgov.conditions WHERE nct_id = %s", (nct_id,)
                    )
                    conditions = [row[0] for row in cur.fetchall()]
                    if not conditions:
                        async with self:
                            self.similar_trials = []
                        return
                    query = """
                    WITH similar_by_condition AS (
                        SELECT DISTINCT c.nct_id,
                               COUNT(*) as matching_conditions
                        FROM ctgov.conditions c
                        WHERE c.name = ANY(%s)
                          AND c.nct_id != %s
                        GROUP BY c.nct_id
                    )
                    SELECT 
                        s.nct_id, s.brief_title, s.overall_status, s.phase, s.enrollment,
                        sbc.matching_conditions
                    FROM ctgov.studies s
                    JOIN similar_by_condition sbc ON s.nct_id = sbc.nct_id
                    WHERE s.phase = %s AND s.study_type = %s
                    ORDER BY sbc.matching_conditions DESC, s.start_date DESC NULLS LAST
                    LIMIT 5
                    """
                    cur.execute(
                        query,
                        (
                            conditions,
                            nct_id,
                            trial_data.get("phase"),
                            trial_data.get("study_type"),
                        ),
                    )
                    similar_trials_data = [
                        dict(zip([desc[0] for desc in cur.description], row))
                        for row in cur.fetchall()
                    ]
                    async with self:
                        self.similar_trials = similar_trials_data
        except Exception as e:
            logging.exception(f"Error fetching similar trials: {e}")
        finally:
            if conn:
                return_db_connection(conn)

    @rx.event(background=True)
    async def fetch_sponsor_portfolio(self, trial_data: TrialDetail):
        lead_sponsor = next(
            (
                s
                for s in trial_data.get("sponsors", [])
                if s.get("lead_or_collaborator") == "lead"
            ),
            None,
        )
        if not lead_sponsor:
            async with self:
                self.sponsor_portfolio = []
            return
        sponsor_name = lead_sponsor.get("name")
        current_nct_id = trial_data.get("nct_id")
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    query = """
                    SELECT s.nct_id, s.brief_title, s.overall_status, s.phase
                    FROM ctgov.studies s
                    JOIN ctgov.sponsors sp ON s.nct_id = sp.nct_id
                    WHERE sp.name = %s AND sp.lead_or_collaborator = 'lead' AND s.nct_id != %s
                    ORDER BY s.start_date DESC NULLS LAST
                    LIMIT 5
                    """
                    cur.execute(query, (sponsor_name, current_nct_id))
                    portfolio_data = [
                        dict(zip([desc[0] for desc in cur.description], row))
                        for row in cur.fetchall()
                    ]
                    async with self:
                        self.sponsor_portfolio = portfolio_data
        except Exception as e:
            logging.exception(f"Error fetching sponsor portfolio: {e}")
        finally:
            if conn:
                return_db_connection(conn)