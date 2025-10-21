import reflex as rx
import uuid
import datetime
from typing import cast
from app.models.workspace import (
    Workspace,
    WorkspaceMember,
    WorkspaceTrial,
    WorkspaceActivity,
)
from app.states.auth_state import AuthState

_workspaces_db: dict[str, Workspace] = {}
_user_workspaces_db: dict[str, set[str]] = {}


class WorkspaceState(rx.State):
    workspaces: list[Workspace] = []
    is_loading: bool = False
    show_create_dialog: bool = False
    is_creating: bool = False

    async def _get_user_email(self) -> str | None:
        auth_state = await self.get_state(AuthState)
        if auth_state.user:
            return auth_state.user.get("email")
        return None

    @rx.event(background=True)
    async def load_workspaces(self):
        user_email = None
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            if auth_state.user:
                user_email = auth_state.user.get("email")
        if user_email:
            user_workspace_ids = _user_workspaces_db.get(user_email, set())
            user_workspaces_list = [
                _workspaces_db[ws_id]
                for ws_id in user_workspace_ids
                if ws_id in _workspaces_db
            ]
            async with self:
                self.workspaces = sorted(
                    user_workspaces_list, key=lambda w: w["last_updated"], reverse=True
                )
        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def create_workspace(self, form_data: dict):
        async with self:
            self.is_creating = True
        user_email = await self._get_user_email()
        if not user_email:
            async with self:
                yield rx.toast.error("You must be logged in to create a workspace.")
                self.is_creating = False
            return
        name = form_data.get("name", "").strip()
        if not name:
            async with self:
                yield rx.toast.warning("Workspace name cannot be empty.")
                self.is_creating = False
            return
        try:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            workspace_id = str(uuid.uuid4())
            new_workspace = Workspace(
                workspace_id=workspace_id,
                name=name,
                description=form_data.get("description", ""),
                owner_email=user_email,
                members=[
                    WorkspaceMember(email=user_email, role="owner", joined_date=now)
                ],
                trials=[],
                created_date=now,
                last_updated=now,
                activity=[],
            )
            _workspaces_db[workspace_id] = new_workspace
            if user_email not in _user_workspaces_db:
                _user_workspaces_db[user_email] = set()
            _user_workspaces_db[user_email].add(workspace_id)
            async with self:
                self.workspaces.insert(0, new_workspace)
                self.show_create_dialog = False
                yield rx.toast.success(f"Workspace '{name}' created!")
        except Exception as e:
            logging.exception(f"Failed to create workspace: {e}")
            async with self:
                yield rx.toast.error("An error occurred while creating the workspace.")
        finally:
            async with self:
                self.is_creating = False

    @rx.event
    def set_show_create_dialog(self, show: bool):
        self.show_create_dialog = show

    @rx.event(background=True)
    async def add_trial_to_workspace(self, workspace_id: str, nct_id: str):
        user_email = None
        async with self:
            auth_state = await self.get_state(AuthState)
            if auth_state.user:
                user_email = auth_state.user.get("email")
        if not user_email:
            yield rx.toast.error("You must be logged in.")
            return
        if workspace_id not in _workspaces_db:
            yield rx.toast.error("Workspace not found.")
            return
        workspace = _workspaces_db[workspace_id]
        if user_email not in [m["email"] for m in workspace["members"]]:
            yield rx.toast.error("You are not a member of this workspace.")
            return
        if any((t["nct_id"] == nct_id for t in workspace["trials"])):
            yield rx.toast.info(f"Trial {nct_id} is already in this workspace.")
            return
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        workspace["trials"].append(
            WorkspaceTrial(
                nct_id=nct_id, added_by=user_email, added_date=now, workspace_notes=""
            )
        )
        workspace["last_updated"] = now
        workspace["activity"].insert(
            0,
            WorkspaceActivity(
                activity_id=str(uuid.uuid4()),
                user=user_email,
                action="added trial",
                target=nct_id,
                timestamp=now,
                details=f"Added trial {nct_id}",
            ),
        )
        async with self:
            yield rx.toast.success(
                f"Trial {nct_id} added to workspace '{workspace['name']}'."
            )
            from app.states.workspace_detail_state import WorkspaceDetailState

            yield WorkspaceDetailState.load_workspace