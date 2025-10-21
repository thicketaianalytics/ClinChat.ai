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
    current_workspace_id: str = ""
    is_loading: bool = False
    show_create_dialog: bool = False

    @rx.var
    def current_workspace(self) -> Workspace | None:
        if self.current_workspace_id:
            return _workspaces_db.get(self.current_workspace_id)
        return None

    async def _get_user_email(self) -> str | None:
        auth_state = await self.get_state(AuthState)
        if auth_state.user:
            return auth_state.user["email"]
        return None

    @rx.event(background=True)
    async def load_workspaces(self):
        async with self:
            self.is_loading = True
        user_email = await self._get_user_email()
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
        user_email = await self._get_user_email()
        if not user_email:
            yield rx.toast.error("You must be logged in to create a workspace.")
            return
        name = form_data.get("name", "").strip()
        if not name:
            yield rx.toast.warning("Workspace name cannot be empty.")
            return
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        workspace_id = str(uuid.uuid4())
        new_workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            description=form_data.get("description", ""),
            owner_email=user_email,
            members=[WorkspaceMember(email=user_email, role="owner", joined_date=now)],
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

    @rx.event
    def set_show_create_dialog(self, show: bool):
        self.show_create_dialog = show