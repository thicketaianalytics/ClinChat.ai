from typing import TypedDict, Optional


class Intervention(TypedDict):
    intervention_type: str
    name: str


class Sponsor(TypedDict):
    agency_class: str
    lead_or_collaborator: str
    name: str


class Location(TypedDict):
    facility: str
    status: Optional[str]
    city: str
    state: Optional[str]
    zip: Optional[str]
    country: str


class DesignGroup(TypedDict):
    group_type: str
    title: str
    description: Optional[str]


class DesignOutcome(TypedDict):
    outcome_type: str
    measure: str
    time_frame: str
    description: Optional[str]


class StudyReference(TypedDict):
    citation: str
    reference_type: Optional[str]


class Trial(TypedDict):
    nct_id: str
    brief_title: str
    overall_status: str
    phase: Optional[str]
    enrollment: Optional[int]
    start_date: Optional[str]
    completion_date: Optional[str]
    study_type: Optional[str]
    location_count: int
    intervention_count: int
    primary_therapeutic_area: Optional[str]


class TrialDetail(Trial):
    official_title: Optional[str]
    brief_summary: Optional[str]
    detailed_description: Optional[str]
    eligibility_criteria: Optional[str]
    conditions: Optional[list[str]]
    interventions: Optional[list[Intervention]]
    sponsors: Optional[list[Sponsor]]
    locations: Optional[list[Location]]
    design_groups: Optional[list[DesignGroup]]
    design_outcomes: Optional[list[DesignOutcome]]
    mesh_terms: Optional[list[str]]
    references: Optional[list[StudyReference]]