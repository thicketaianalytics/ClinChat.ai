import reflex as rx
from app.components.sidebar import sidebar
from app.states.ui_state import UIState
from app.states.workspace_detail_state import WorkspaceDetailState


def add_member_dialog() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button(
                rx.icon(tag="user-plus", size=16, class_name="mr-2"),
                "Add Member",
                class_name="flex items-center bg-white text-gray-700 border border-gray-300 text-sm font-medium py-2 px-4 rounded-md hover:bg-gray-50",
            )
        ),
        rx.radix.primitives.dialog.overlay(
            class_name="DialogOverlay fixed inset-0 bg-black/50"
        ),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Add New Member", class_name="text-lg font-semibold text-gray-800"
            ),
            rx.radix.primitives.dialog.description(
                "Enter the email of the person you want to invite.",
                class_name="text-sm text-gray-600 mt-1 mb-4",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "Email", class_name="text-sm font-medium text-gray-700 mb-1"
                    ),
                    rx.el.input(
                        name="email",
                        placeholder="member@example.com",
                        type="email",
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Role", class_name="text-sm font-medium text-gray-700 mb-1"
                    ),
                    rx.el.select(
                        rx.el.option("Viewer", value="viewer"),
                        rx.el.option("Editor", value="editor"),
                        rx.el.option("Owner", value="owner"),
                        name="role",
                        default_value="viewer",
                        class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white",
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
                        "Add Member",
                        type="submit",
                        class_name="bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
                    ),
                    class_name="flex justify-end gap-3",
                ),
                on_submit=WorkspaceDetailState.add_member,
                reset_on_submit=True,
            ),
            class_name="DialogContent fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-md rounded-xl bg-white p-6 shadow-lg",
        ),
        open=WorkspaceDetailState.show_add_member_dialog,
        on_open_change=WorkspaceDetailState.set_show_add_member_dialog,
    )


def add_trial_dialog() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button(
                rx.icon(tag="plus", size=16, class_name="mr-2"),
                "Add Trial",
                class_name="flex items-center bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
            )
        ),
        rx.radix.primitives.dialog.overlay(
            class_name="DialogOverlay fixed inset-0 bg-black/50"
        ),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Add Trial to Workspace",
                class_name="text-lg font-semibold text-gray-800",
            ),
            rx.el.form(
                rx.el.input(
                    name="nct_id",
                    placeholder="Enter NCT ID...",
                    class_name="w-full text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                rx.el.button(
                    "Add Trial",
                    type="submit",
                    class_name="bg-blue-600 text-white font-medium py-2 px-6 rounded-md hover:bg-blue-700",
                ),
                on_submit=WorkspaceDetailState.add_trial_to_current_workspace,
                reset_on_submit=True,
                class_name="flex gap-2 mt-4",
            ),
            class_name="DialogContent fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-md rounded-xl bg-white p-6 shadow-lg",
        ),
        open=WorkspaceDetailState.show_add_trial_dialog,
        on_open_change=WorkspaceDetailState.set_show_add_trial_dialog,
    )


def member_item(member: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.img(
                src=f"https://api.dicebear.com/9.x/initials/svg?seed={member['email']}",
                class_name="h-10 w-10 rounded-full",
            ),
            rx.el.div(
                rx.el.p(
                    member["email"], class_name="text-sm font-medium text-gray-800"
                ),
                rx.el.p(
                    f"Joined on {member['joined_date'].split('T')[0]}",
                    class_name="text-xs text-gray-500",
                ),
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.span(
                member["role"].capitalize(),
                class_name="text-sm font-medium text-gray-600",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg",
    )


def workspace_detail_header(workspace: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(workspace["name"], class_name="text-2xl font-bold text-gray-800"),
            rx.el.p(workspace["description"], class_name="text-gray-600 mt-1"),
            rx.el.div(
                rx.el.div(
                    rx.icon(tag="users", size=14, class_name="text-gray-500"),
                    rx.el.span(
                        f"{workspace['members'].length()} Members",
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                rx.el.div(
                    rx.icon(tag="file-text", size=14, class_name="text-gray-500"),
                    rx.el.span(
                        f"{workspace['trials'].length()} Trials",
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                class_name="flex items-center gap-4 mt-2",
            ),
        ),
        rx.el.div(
            add_member_dialog(),
            add_trial_dialog(),
            class_name="flex items-center gap-2",
        ),
        class_name="flex justify-between items-start mb-6",
    )


def workspace_detail_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.cond(
                WorkspaceDetailState.is_loading,
                rx.el.div(
                    rx.spinner(size="3"),
                    class_name="flex justify-center items-center h-full",
                ),
                rx.cond(
                    WorkspaceDetailState.workspace.is_not_none(),
                    rx.el.div(
                        workspace_detail_header(WorkspaceDetailState.workspace),
                        rx.el.div(
                            rx.el.div(
                                rx.el.h2(
                                    "Trials",
                                    class_name="text-xl font-semibold text-gray-800 mb-4",
                                ),
                                class_name="lg:col-span-2",
                            ),
                            rx.el.div(
                                rx.el.h2(
                                    "Members",
                                    class_name="text-xl font-semibold text-gray-800 mb-4",
                                ),
                                rx.el.div(
                                    rx.foreach(
                                        WorkspaceDetailState.workspace["members"],
                                        member_item,
                                    ),
                                    class_name="space-y-3",
                                ),
                                class_name="lg:col-span-1",
                            ),
                            class_name="grid lg:grid-cols-3 gap-6",
                        ),
                    ),
                    rx.el.div(
                        "Workspace not found or you do not have access.",
                        class_name="text-center text-gray-500",
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