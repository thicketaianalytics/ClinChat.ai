from typing import TypedDict, Optional


class WorkspaceMember(TypedDict):
    email: str
    role: str
    joined_date: str


class WorkspaceTrial(TypedDict):
    nct_id: str
    added_by: str
    added_date: str
    workspace_notes: str


class WorkspaceActivity(TypedDict):
    activity_id: str
    user: str
    action: str
    target: str
    timestamp: str
    details: str


class Workspace(TypedDict):
    workspace_id: str
    name: str
    description: str
    owner_email: str
    members: list[WorkspaceMember]
    trials: list[WorkspaceTrial]
    created_date: str
    last_updated: str
    activity: list[WorkspaceActivity]