import reflex as rx
from app.states.comparison_state import ComparisonState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar


def selected_trial_chip(nct_id: str) -> rx.Component:
    return rx.el.span(
        nct_id,
        rx.el.button(
            rx.icon(tag="x", size=14),
            on_click=lambda: ComparisonState.remove_trial_from_comparison(nct_id),
            class_name="ml-1.5 p-0.5 rounded-full hover:bg-red-200 text-red-700",
        ),
        class_name="flex items-center bg-red-100 text-red-800 text-sm font-medium px-2.5 py-1 rounded-full",
    )


def comparison_header(trial: rx.Var[dict]) -> rx.Component:
    return rx.el.th(
        rx.el.div(
            rx.el.a(
                trial["nct_id"],
                href=f"/trial/{trial['nct_id']}",
                class_name="font-semibold text-blue-600 hover:underline",
            ),
            rx.el.p(
                trial["brief_title"],
                class_name="text-xs font-normal text-gray-600 mt-1 truncate",
                max_width="200px",
            ),
            class_name="p-3 text-left",
        ),
        class_name="sticky top-0 bg-gray-50/75 backdrop-blur-sm z-10 border-b border-gray-200",
    )


def comparison_row(field_name: str, key: str) -> rx.Component:
    return rx.el.tr(
        rx.el.td(field_name, class_name="p-3 font-medium text-sm text-gray-700"),
        rx.foreach(
            ComparisonState.comparison_data,
            lambda trial: rx.el.td(
                trial[key].to_string(),
                class_name="p-3 text-sm text-gray-600 border-l border-gray-200",
            ),
        ),
        class_name="border-t border-gray-200 hover:bg-gray-50",
    )


def comparison_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(
                        "Feature",
                        class_name="p-3 text-left text-sm font-semibold text-gray-800 sticky top-0 bg-gray-50/75 backdrop-blur-sm z-10 border-b border-gray-200",
                    ),
                    rx.foreach(ComparisonState.comparison_data, comparison_header),
                )
            ),
            rx.el.tbody(
                comparison_row("Status", "overall_status"),
                comparison_row("Phase", "phase"),
                comparison_row("Study Type", "study_type"),
                comparison_row("Enrollment", "enrollment"),
                comparison_row("Start Date", "start_date"),
                comparison_row("Completion Date", "completion_date"),
            ),
            class_name="w-full table-fixed",
        ),
        class_name="overflow-x-auto bg-white border border-gray-200 rounded-xl shadow-sm",
    )


def compare_page() -> rx.Component:
    """The UI for the Cross Trials Comparison page."""
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Cross Trials Comparison",
                    class_name="text-2xl font-bold text-gray-800",
                ),
                rx.el.p(
                    "Select 2 to 5 trials to compare their key attributes side-by-side.",
                    class_name="text-gray-600",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.h3(
                    "Select Trials to Compare",
                    class_name="text-lg font-semibold text-gray-800 mb-3",
                ),
                rx.el.form(
                    rx.el.input(
                        name="nct_id",
                        placeholder="Enter NCT ID (e.g., NCT...)",
                        class_name="flex-grow text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500",
                    ),
                    rx.el.button(
                        rx.icon(tag="plus", size=16),
                        "Add Trial",
                        type="submit",
                        class_name="flex items-center gap-2 bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
                    ),
                    on_submit=ComparisonState.handle_add_trial_submit,
                    reset_on_submit=True,
                    class_name="flex items-center gap-3 mb-4",
                ),
                rx.cond(
                    ComparisonState.selected_nct_ids.length() > 0,
                    rx.el.div(
                        rx.el.p(
                            f"{ComparisonState.selected_nct_ids.length()} of 5 trials selected",
                            class_name="text-sm font-medium text-gray-600",
                        ),
                        rx.el.div(
                            rx.foreach(
                                ComparisonState.selected_nct_ids, selected_trial_chip
                            ),
                            class_name="flex flex-wrap gap-2",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Clear All",
                                on_click=ComparisonState.clear_comparison,
                                class_name="text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-md",
                            ),
                            rx.el.button(
                                "Export to CSV",
                                on_click=ComparisonState.export_comparison_csv,
                                class_name="text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-3 py-1.5 rounded-md border border-gray-300",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        class_name="flex items-center justify-between gap-4 p-3 bg-gray-50 border border-gray-200 rounded-lg",
                    ),
                ),
                class_name="p-4 bg-white border rounded-xl shadow-sm mb-6",
            ),
            rx.cond(
                ComparisonState.is_loading,
                rx.el.div(rx.spinner(size="3"), class_name="flex justify-center p-16"),
                rx.cond(
                    ComparisonState.comparison_data.length() > 0,
                    comparison_table(),
                    rx.el.div(
                        rx.icon(
                            "git-compare-arrows",
                            size=48,
                            class_name="text-gray-400 mx-auto",
                        ),
                        rx.el.h3(
                            "Start Comparing Trials",
                            class_name="mt-4 text-lg font-semibold text-gray-800",
                        ),
                        rx.el.p(
                            "Add NCT IDs above or select trials from 'My Trials' to begin.",
                            class_name="mt-1 text-sm text-gray-500",
                        ),
                        rx.el.a(
                            "Go to My Trials",
                            href="/my-trials",
                            class_name="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700",
                        ),
                        class_name="text-center py-16 px-6 bg-white rounded-xl border border-dashed border-gray-300 shadow-sm",
                    ),
                ),
            ),
            class_name=rx.cond(
                UIState.sidebar_collapsed,
                "p-8 flex-1 md:ml-20 transition-all duration-300",
                "p-8 flex-1 md:ml-64 transition-all duration-300",
            ),
        ),
        class_name="flex font-['DM_Sans'] bg-gray-50 min-h-screen",
    )