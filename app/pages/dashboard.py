import reflex as rx
from app.states.auth_state import AuthState
from app.states.dashboard_state import DashboardState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar
from app.components.loading_skeletons import metric_card_skeleton


def metric_card(title: str, value: rx.Var[str], icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(tag=icon, class_name="text-gray-500"),
            class_name="p-2 bg-gray-100 rounded-md w-fit",
        ),
        rx.el.h3(title, class_name="text-sm font-medium text-gray-500 mt-2"),
        rx.el.p(value, class_name="text-2xl font-bold text-gray-800"),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
    )


def quick_action_button(text: str, icon: str, href: str) -> rx.Component:
    return rx.el.a(
        rx.icon(tag=icon, class_name="mr-2"),
        text,
        href=href,
        class_name="flex items-center justify-center px-4 py-2 bg-white text-sm font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
    )


def trial_item(trial: rx.Var[dict]) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    trial["nct_id"], class_name="text-sm font-semibold text-blue-600"
                ),
                rx.el.span(
                    trial["overall_status"],
                    class_name=rx.cond(
                        trial["overall_status"] == "RECRUITING",
                        "text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded-full",
                        rx.cond(
                            trial["overall_status"] == "COMPLETED",
                            "text-xs font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded-full",
                            "text-xs font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded-full",
                        ),
                    ),
                ),
                class_name="flex justify-between items-center mb-2",
            ),
            rx.el.p(
                trial["brief_title"],
                class_name="font-semibold text-sm text-gray-800 truncate h-10 leading-tight",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.icon(tag="flask-round", size=14, class_name="text-gray-500"),
                rx.el.p(trial.get("phase", "N/A"), class_name="text-xs text-gray-600"),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.div(
                rx.icon(tag="users", size=14, class_name="text-gray-500"),
                rx.el.p(
                    trial.get("enrollment", "N/A").to_string(),
                    class_name="text-xs text-gray-600",
                ),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.div(
                rx.icon(tag="calendar", size=14, class_name="text-gray-500"),
                rx.el.p(
                    trial.get("start_date", "N/A"), class_name="text-xs text-gray-600"
                ),
                class_name="flex items-center gap-1.5",
            ),
            class_name="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-100",
        ),
        href=f"/trial/{trial['nct_id']}",
        class_name="flex flex-col p-4 bg-white rounded-lg border border-gray-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300",
    )


def dashboard_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Dashboard", class_name="text-2xl font-bold text-gray-800"
                    ),
                    rx.el.p(
                        "Overview of clinical trials data.", class_name="text-gray-600"
                    ),
                ),
                rx.el.div(
                    rx.el.div(
                        rx.cond(
                            AuthState.user,
                            rx.el.div(
                                rx.el.p(
                                    AuthState.user["email"],
                                    class_name="text-sm font-medium text-right",
                                ),
                                class_name="hidden md:block",
                            ),
                        ),
                        rx.el.button(
                            "Logout",
                            rx.icon(tag="log-out", class_name="ml-2", size=16),
                            on_click=AuthState.logout,
                            class_name="flex items-center bg-red-500 text-white px-3 py-1.5 text-sm rounded-md hover:bg-red-600 transition-colors",
                        ),
                        class_name="flex items-center gap-4",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex justify-between items-start mb-8",
            ),
            rx.cond(
                DashboardState.is_loading,
                rx.el.div(
                    rx.foreach([1, 2, 3, 4, 5, 6, 7], lambda i: metric_card_skeleton()),
                    class_name="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8",
                ),
                rx.el.div(
                    metric_card(
                        "Total Trials",
                        DashboardState.total_trials.to_string(),
                        "bar-chart-2",
                    ),
                    metric_card(
                        "Active Trials",
                        DashboardState.active_trials.to_string(),
                        "loader",
                    ),
                    metric_card(
                        "Completed Trials",
                        DashboardState.completed_trials.to_string(),
                        "check_check",
                    ),
                    metric_card(
                        "Phase 1 Trials",
                        DashboardState.phase_1_trials.to_string(),
                        "beaker",
                    ),
                    metric_card(
                        "Phase 2 Trials",
                        DashboardState.phase_2_trials.to_string(),
                        "test_tube",
                    ),
                    metric_card(
                        "Phase 3 Trials",
                        DashboardState.phase_3_trials.to_string(),
                        "test-tubes",
                    ),
                    metric_card(
                        "Phase 4 Trials",
                        DashboardState.phase_4_trials.to_string(),
                        "award",
                    ),
                    class_name="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8",
                ),
            ),
            rx.el.div(
                quick_action_button("Browse All Trials", "search", "/browse"),
                quick_action_button("View My Saved Trials", "bookmark", "/my-trials"),
                quick_action_button("Compare Trials", "git-compare-arrows", "/compare"),
                class_name="flex items-center gap-4 mb-8",
            ),
            rx.el.div(
                rx.el.h2(
                    "Recent Updates",
                    class_name="text-xl font-semibold text-gray-800 mb-4",
                ),
                rx.el.div(
                    rx.cond(
                        DashboardState.is_loading,
                        rx.el.div(
                            rx.el.div(
                                class_name="h-12 bg-gray-200 rounded-lg animate-pulse"
                            ),
                            rx.el.div(
                                class_name="h-12 bg-gray-200 rounded-lg animate-pulse"
                            ),
                            rx.el.div(
                                class_name="h-12 bg-gray-200 rounded-lg animate-pulse"
                            ),
                            rx.el.div(
                                class_name="h-12 bg-gray-200 rounded-lg animate-pulse"
                            ),
                            rx.el.div(
                                class_name="h-12 bg-gray-200 rounded-lg animate-pulse"
                            ),
                            class_name="space-y-3",
                        ),
                        rx.el.div(
                            rx.foreach(DashboardState.recent_trials, trial_item),
                            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4",
                        ),
                    ),
                    class_name="space-y-3",
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