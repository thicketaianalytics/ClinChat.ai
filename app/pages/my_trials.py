import reflex as rx
from app.states.saved_trials_state import SavedTrialsState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar
import datetime
from app.states.report_state import ReportState
from app.components.loading_skeletons import trial_card_skeleton
from app.components.empty_state import empty_state
from app.components.tooltip_wrapper import tooltip


def tag_badge(tag: str, nct_id: str) -> rx.Component:
    color_map = {
        "High Priority": "bg-blue-100 text-blue-800",
        "Under Review": "bg-yellow-100 text-yellow-800",
        "Archived": "bg-gray-100 text-gray-800",
        "To Compare": "bg-purple-100 text-purple-800",
    }
    return rx.el.span(
        tag,
        rx.el.button(
            rx.icon(tag="x", size=12),
            on_click=lambda: SavedTrialsState.remove_tag(nct_id, tag),
            class_name="ml-1.5 opacity-50 hover:opacity-100",
            aria_label=f"Remove tag {tag}",
        ),
        class_name=f"{color_map.get(tag, 'bg-gray-100 text-gray-800')} text-xs font-medium inline-flex items-center px-2 py-0.5 rounded-full",
    )


def saved_trial_card(trial: rx.Var[dict]) -> rx.Component:
    nct_id = trial["nct_id"]
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                type="checkbox",
                checked=SavedTrialsState.selected_nct_ids.contains(nct_id),
                on_change=lambda: SavedTrialsState.toggle_selection(nct_id),
                class_name="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500",
            ),
            rx.el.div(
                rx.el.p(nct_id, class_name="text-sm font-semibold text-blue-600"),
                rx.el.span(
                    trial["overall_status"],
                    class_name=rx.cond(
                        trial["overall_status"] == "RECRUITING",
                        "text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded-full",
                        "text-xs font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded-full",
                    ),
                ),
                class_name="flex justify-between items-center mb-1.5",
            ),
            class_name="flex items-start gap-3",
        ),
        rx.el.h3(
            trial["brief_title"],
            class_name="font-semibold text-gray-800 text-base leading-tight h-10 overflow-hidden mt-1",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Phase", class_name="text-xs text-gray-500"),
                rx.el.p(trial.get("phase", "N/A"), class_name="text-sm font-medium"),
            ),
            rx.el.div(
                rx.el.p("Enrollment", class_name="text-xs text-gray-500"),
                rx.el.p(
                    trial.get("enrollment", "N/A"), class_name="text-sm font-medium"
                ),
            ),
            class_name="grid grid-cols-2 gap-2 text-center border-t border-gray-200 py-2 my-2",
        ),
        rx.el.div(
            rx.el.h4("Tags", class_name="text-xs font-medium text-gray-600 mb-1"),
            rx.el.div(
                rx.foreach(trial.get("tags", []), lambda tag: tag_badge(tag, nct_id)),
                class_name="flex flex-wrap gap-1",
            ),
            class_name="mb-3",
        ),
        rx.el.div(
            rx.el.h4("Notes", class_name="text-xs font-medium text-gray-600 mb-1"),
            rx.el.textarea(
                default_value=trial.get("notes", ""),
                on_blur=lambda notes: SavedTrialsState.update_notes(nct_id, notes),
                placeholder="Add notes...",
                class_name="w-full text-sm border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none h-20",
            ),
        ),
        rx.el.div(
            rx.el.a(
                rx.icon(tag="arrow-right", size=16),
                "View Details",
                href=f"/trial/{nct_id}",
                class_name="flex items-center gap-2 w-full justify-center text-sm font-medium text-blue-600 hover:text-blue-700 px-3 py-2 rounded-md transition-colors",
            ),
            tooltip(
                "Remove from My Trials",
                rx.el.button(
                    rx.icon(tag="trash-2", size=16),
                    on_click=lambda: SavedTrialsState.remove_trial(nct_id),
                    class_name="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors",
                    aria_label="Remove trial",
                ),
                side="bottom",
            ),
            class_name="mt-2 flex justify-between items-center border-t border-gray-200 pt-2",
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col h-full",
    )


def bulk_actions_bar() -> rx.Component:
    return rx.cond(
        SavedTrialsState.selected_nct_ids.length() > 0,
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    f"{SavedTrialsState.selected_nct_ids.length()} selected",
                    class_name="text-sm font-medium text-gray-700",
                ),
                class_name="flex items-center gap-4",
            ),
            rx.el.div(
                rx.el.button(
                    "Remove Selected",
                    on_click=SavedTrialsState.bulk_remove,
                    class_name="text-sm font-medium text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-md",
                ),
                rx.el.select(
                    rx.el.option("Add Tag to Selected...", value="", disabled=True),
                    rx.foreach(
                        SavedTrialsState.available_tags_for_bulk_add,
                        lambda tag: rx.el.option(tag, value=tag),
                    ),
                    on_change=SavedTrialsState.bulk_add_tag,
                    value="",
                    class_name="text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-blue-500 focus:border-blue-500",
                ),
                rx.el.button(
                    "Compare Selected",
                    on_click=SavedTrialsState.go_to_comparison,
                    class_name="text-sm font-medium bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex justify-between items-center p-3 bg-gray-50 border border-gray-200 rounded-xl mb-6 sticky top-4 z-10",
        ),
    )


def my_trials_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "My Saved Trials", class_name="text-2xl font-bold text-gray-800"
                ),
                rx.el.p(
                    f"{SavedTrialsState.saved_trials.length()} trials saved.",
                    class_name="text-gray-600",
                ),
                rx.el.div(
                    rx.el.button(
                        "Export All to CSV",
                        on_click=SavedTrialsState.export_to_csv,
                        is_loading=SavedTrialsState.is_exporting_csv,
                        class_name="text-sm font-medium bg-white text-gray-700 border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50",
                    ),
                    rx.el.button(
                        "Export as Excel",
                        on_click=ReportState.generate_saved_trials_excel,
                        is_loading=ReportState.is_generating_excel,
                        class_name="text-sm font-medium bg-white text-gray-700 border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex justify-between items-center mb-4",
            ),
            rx.el.div(
                rx.foreach(
                    SavedTrialsState.available_tags,
                    lambda tag: rx.el.button(
                        tag,
                        on_click=lambda: SavedTrialsState.set_filter_tag(tag),
                        class_name=rx.cond(
                            SavedTrialsState.filter_tag == tag,
                            "px-3 py-1.5 text-sm font-semibold text-white bg-blue-600 rounded-full",
                            "px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-gray-50",
                        ),
                    ),
                ),
                class_name="flex items-center gap-2 mb-6",
            ),
            bulk_actions_bar(),
            rx.cond(
                SavedTrialsState.is_loading,
                rx.el.div(
                    rx.foreach([1, 2, 3], lambda i: trial_card_skeleton()),
                    class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-6",
                ),
                rx.cond(
                    SavedTrialsState.filtered_trials.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            SavedTrialsState.filtered_trials,
                            lambda trial: rx.fragment(
                                saved_trial_card(trial), key=trial["nct_id"]
                            ),
                        ),
                        class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-6",
                    ),
                    empty_state(
                        icon="bookmark-plus",
                        title="No Saved Trials Yet",
                        description="Browse trials and click the bookmark icon to save them here.",
                        button_text="Browse Trials",
                        href="/browse",
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