import reflex as rx
from app.states.workspace_state import WorkspaceState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar
from app.components.empty_state import empty_state


def create_workspace_dialog() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button(
                rx.icon(tag="plus", size=16, class_name="mr-2"),
                "Create New Workspace",
                class_name="flex items-center bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
            )
        ),
        rx.radix.primitives.dialog.overlay(
            class_name="DialogOverlay fixed inset-0 bg-black/50"
        ),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Create New Workspace", class_name="text-lg font-semibold text-gray-800"
            ),
            rx.radix.primitives.dialog.description(
                "Give your new workspace a name and an optional description.",
                class_name="text-sm text-gray-600 mt-1 mb-4",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "Workspace Name",
                        class_name="text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.input(
                        name="name",
                        placeholder="e.g., Oncology Research Team",
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Description (Optional)",
                        class_name="text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.textarea(
                        name="description",
                        placeholder="A brief summary of what this workspace is for.",
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            class_name="bg-gray-100 text-gray-700 text-sm font-medium py-2 px-4 rounded-md hover:bg-gray-200",
                            type="button",
                        )
                    ),
                    rx.el.button(
                        "Create Workspace",
                        type="submit",
                        is_loading=WorkspaceState.is_creating,
                        class_name="bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
                    ),
                    class_name="flex justify-end gap-3",
                ),
                on_submit=WorkspaceState.create_workspace,
                reset_on_submit=True,
            ),
            class_name="DialogContent fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-md rounded-xl bg-white p-6 shadow-lg",
        ),
        open=WorkspaceState.show_create_dialog,
        on_open_change=WorkspaceState.set_show_create_dialog,
    )


def workspace_card(workspace: rx.Var[dict]) -> rx.Component:
    return rx.el.a(
        rx.el.h3(
            workspace["name"], class_name="text-lg font-semibold text-gray-800 mb-1"
        ),
        rx.el.p(
            workspace["description"],
            class_name="text-sm text-gray-600 h-10 overflow-hidden",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon(tag="users", size=14, class_name="text-gray-500"),
                rx.el.span(
                    f"{workspace['members'].length()} Members",
                    class_name="text-xs text-gray-600",
                ),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.div(
                rx.icon(tag="file-text", size=14, class_name="text-gray-500"),
                rx.el.span(
                    f"{workspace['trials'].length()} Trials",
                    class_name="text-xs text-gray-600",
                ),
                class_name="flex items-center gap-1.5",
            ),
            class_name="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100",
        ),
        href=f"/workspaces/{workspace['workspace_id']}",
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col hover:shadow-lg hover:border-blue-300 hover:-translate-y-1 transition-all duration-300",
    )


def workspaces_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1("Workspaces", class_name="text-2xl font-bold text-gray-800"),
                rx.el.p(
                    "Collaborate with your team by sharing and annotating clinical trials.",
                    class_name="text-gray-600",
                ),
                create_workspace_dialog(),
                class_name="flex justify-between items-center mb-6",
            ),
            rx.cond(
                WorkspaceState.is_loading,
                rx.el.div(
                    rx.spinner(size="3"),
                    class_name="flex justify-center items-center h-96",
                ),
                rx.cond(
                    WorkspaceState.workspaces.length() > 0,
                    rx.el.div(
                        rx.foreach(WorkspaceState.workspaces, workspace_card),
                        class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-6",
                    ),
                    empty_state(
                        icon="users",
                        title="Create Your First Workspace",
                        description="Get started by creating a workspace to collaborate with your team.",
                        button_text="Create Workspace",
                        button_action=WorkspaceState.set_show_create_dialog(True),
                    ),
                ),
            ),
            id="main-content",
            class_name=rx.cond(
                UIState.sidebar_collapsed,
                "p-8 flex-1 md:ml-20 transition-all duration-300 fade-in-content",
                "p-8 flex-1 md:ml-64 transition-all duration-300 fade-in-content",
            ),
        ),
        class_name="flex font-['DM_Sans'] bg-gray-50 min-h-screen",
    )