import reflex as rx
import uuid
import datetime
from typing import cast, Optional
from app.models.workspace import (
    Workspace,
    WorkspaceMember,
    WorkspaceTrial,
    WorkspaceActivity,
)
from app.models.trial import Trial
from app.states.auth_state import AuthState
from app.utils.db import get_db_connection, return_db_connection
from app.states.workspace_state import _workspaces_db, _user_workspaces_db


class WorkspaceDetailState(rx.State):
    workspace: Optional[Workspace] = None
    workspace_trials: list[Trial] = []
    is_loading: bool = True
    show_add_member_dialog: bool = False
    show_add_trial_dialog: bool = False

    @rx.var
    def _workspace_id_from_route(self) -> str:
        return self.router.page.params.get("workspace_id", "")

    @rx.event(background=True)
    async def load_workspace(self):
        async with self:
            self.is_loading = True
            self.workspace = None
            self.workspace_trials = []
            workspace_id = self.router.page.params.get("workspace_id", "")
        if not workspace_id:
            async with self:
                self.is_loading = False
            return
        if workspace_id in _workspaces_db:
            workspace_data = _workspaces_db[workspace_id]
            nct_ids = [t["nct_id"] for t in workspace_data["trials"]]
            trials = []
            if nct_ids:
                conn = None
                try:
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            placeholders = ",".join(["%s"] * len(nct_ids))
                            query = f"SELECT nct_id, brief_title, overall_status, phase, enrollment, start_date FROM ctgov.studies WHERE nct_id IN ({placeholders})"
                            cur.execute(query, nct_ids)
                            trials = [
                                dict(zip([desc[0] for desc in cur.description], row))
                                for row in cur.fetchall()
                            ]
                except Exception as e:
                    logging.exception(f"Error fetching workspace trials: {e}")
                finally:
                    if conn:
                        return_db_connection(conn)
            async with self:
                self.workspace = workspace_data
                self.workspace_trials = [cast(Trial, t) for t in trials]
        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def add_member(self, form_data: dict):
        async with self:
            email = form_data.get("email", "").strip()
            role = form_data.get("role", "viewer")
            if not self.workspace or not email:
                yield rx.toast.error("Invalid data.")
                return
            if email in [m["email"] for m in self.workspace["members"]]:
                yield rx.toast.info(f"{email} is already a member.")
                return
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            new_member = WorkspaceMember(email=email, role=role, joined_date=now)
            self.workspace["members"].append(new_member)
            self.workspace["last_updated"] = now
            self.workspace["activity"].insert(
                0,
                WorkspaceActivity(
                    activity_id=str(uuid.uuid4()),
                    user=email,
                    action="joined workspace",
                    target=email,
                    timestamp=now,
                    details=f"{email} was added as a {role}",
                ),
            )
            if email not in _user_workspaces_db:
                _user_workspaces_db[email] = set()
            _user_workspaces_db[email].add(self.workspace["workspace_id"])
            self.show_add_member_dialog = False
            yield rx.toast.success(f"{email} added to workspace.")
        yield WorkspaceDetailState.load_workspace

    @rx.event
    def set_show_add_member_dialog(self, show: bool):
        self.show_add_member_dialog = show

    @rx.event
    def set_show_add_trial_dialog(self, show: bool):
        self.show_add_trial_dialog = show

    @rx.event(background=True)
    async def add_trial_to_current_workspace(self, form_data: dict):
        nct_id = form_data.get("nct_id", "").strip()
        if not nct_id or not self.workspace:
            yield rx.toast.warning("NCT ID is required.")
            return
        from app.states.workspace_state import WorkspaceState

        yield WorkspaceState.add_trial_to_workspace(
            self.workspace["workspace_id"], nct_id
        )
        async with self:
            self.show_add_trial_dialog = False