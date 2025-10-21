import reflex as rx
from app.states.browse_state import BrowseState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar


def filter_input(
    label: str, placeholder: str, name: str, value: rx.Var[str]
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="text-xs font-medium text-gray-600 mb-1"),
        rx.el.input(
            name=name,
            placeholder=placeholder,
            default_value=value,
            on_change=lambda val: BrowseState.set_search_term(name, val),
            class_name="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500",
        ),
    )


def filter_select(
    label: str, name: str, value: rx.Var[str], options: rx.Var[list[str]]
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="text-xs font-medium text-gray-600 mb-1"),
        rx.el.select(
            rx.el.option("All", value=""),
            rx.foreach(options, lambda opt: rx.el.option(opt, value=opt)),
            name=name,
            value=value,
            on_change=lambda val: BrowseState.set_search_term(name, val),
            class_name="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white",
        ),
    )


def trial_card(trial: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
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
            rx.el.h3(
                trial["brief_title"],
                class_name="font-semibold text-gray-800 text-base leading-tight h-10 overflow-hidden",
            ),
            rx.cond(
                trial.get("primary_therapeutic_area"),
                rx.el.div(
                    rx.icon(tag="tag", size=14, class_name="text-gray-500"),
                    rx.el.p(
                        trial.get("primary_therapeutic_area", "N/A"),
                        class_name="text-xs text-gray-600 truncate",
                    ),
                    class_name="flex items-center gap-1.5 mt-2",
                ),
            ),
            class_name="flex-1 mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Phase", class_name="text-xs text-gray-500"),
                rx.el.p(trial.get("phase", "N/A"), class_name="text-sm font-medium"),
            ),
            rx.el.div(
                rx.el.p("Enrollment", class_name="text-xs text-gray-500"),
                rx.el.p(
                    trial.get("enrollment", "N/A").to_string(),
                    class_name="text-sm font-medium",
                ),
            ),
            rx.el.div(
                rx.el.p("Locations", class_name="text-xs text-gray-500"),
                rx.el.p(
                    trial["location_count"].to_string(),
                    class_name="text-sm font-medium",
                ),
            ),
            rx.el.div(
                rx.el.p("Interventions", class_name="text-xs text-gray-500"),
                rx.el.p(
                    trial["intervention_count"].to_string(),
                    class_name="text-sm font-medium",
                ),
            ),
            class_name="grid grid-cols-2 gap-y-3 gap-x-2 text-center border-t border-b border-gray-200 py-3",
        ),
        rx.el.div(
            rx.el.a(
                rx.icon(tag="arrow-right", size=16),
                "View Details",
                href=f"/trial/{trial['nct_id']}",
                class_name="flex items-center gap-2 w-full justify-center text-sm font-medium text-blue-600 hover:text-blue-700 px-3 py-2 rounded-md transition-colors",
            ),
            rx.el.button(
                rx.icon(tag="bookmark", size=16),
                on_click=lambda: BrowseState.bookmark_trial(trial["nct_id"]),
                class_name="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors",
            ),
            class_name="mt-2 flex justify-between items-center",
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 h-full position: 'relative'",
    )


def browse_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Browse Clinical Trials",
                    class_name="text-2xl font-bold text-gray-800",
                ),
                rx.el.p(
                    f"{BrowseState.total_trials.to_string()} trials found.",
                    class_name="text-gray-600",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Filters", class_name="text-lg font-semibold text-gray-800"
                        ),
                        rx.el.button(
                            rx.icon(
                                tag=rx.cond(
                                    UIState.filters_collapsed,
                                    "chevron-down",
                                    "chevron-up",
                                ),
                                size=20,
                            ),
                            on_click=UIState.toggle_filters,
                            class_name="text-gray-600 hover:bg-gray-100 rounded-md p-1",
                        ),
                        class_name="flex items-center justify-between mb-4",
                    ),
                    rx.cond(
                        ~UIState.filters_collapsed,
                        rx.el.form(
                            rx.el.div(
                                filter_input(
                                    "NCT ID",
                                    "e.g., NCT...",
                                    "nct_id",
                                    BrowseState.search_terms["nct_id"],
                                ),
                                filter_input(
                                    "Condition",
                                    "e.g., Cancer",
                                    "condition",
                                    BrowseState.search_terms["condition"],
                                ),
                                filter_input(
                                    "Intervention",
                                    "e.g., Aspirin",
                                    "intervention",
                                    BrowseState.search_terms["intervention"],
                                ),
                                filter_input(
                                    "Sponsor",
                                    "e.g., Pfizer",
                                    "sponsor",
                                    BrowseState.search_terms["sponsor"],
                                ),
                                class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-4",
                            ),
                            rx.el.div(
                                filter_select(
                                    "Status",
                                    "status",
                                    BrowseState.search_terms["status"],
                                    BrowseState.filter_options["statuses"],
                                ),
                                filter_select(
                                    "Phase",
                                    "phase",
                                    BrowseState.search_terms["phase"],
                                    BrowseState.filter_options["phases"],
                                ),
                                filter_select(
                                    "Study Type",
                                    "study_type",
                                    BrowseState.search_terms["study_type"],
                                    BrowseState.filter_options["study_types"],
                                ),
                                class_name="grid md:grid-cols-3 gap-4 mt-4",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Search",
                                    type="submit",
                                    class_name="w-full sm:w-auto bg-blue-600 text-white font-medium py-2 px-6 rounded-md hover:bg-blue-700",
                                ),
                                rx.el.button(
                                    "Reset",
                                    type="button",
                                    on_click=BrowseState.reset_filters,
                                    class_name="w-full sm:w-auto bg-gray-200 text-gray-700 font-medium py-2 px-6 rounded-md hover:bg-gray-300",
                                ),
                                class_name="flex gap-4 mt-4 justify-end",
                            ),
                            on_submit=BrowseState.handle_search,
                            class_name="w-full",
                        ),
                    ),
                    class_name="p-4 bg-white border border-gray-200 rounded-xl shadow-sm mb-6 transition-all duration-300",
                ),
                rx.cond(
                    BrowseState.is_table_loading,
                    rx.el.div(
                        rx.spinner(size="3"),
                        class_name="flex items-center justify-center h-96",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.foreach(BrowseState.trials, trial_card),
                            class_name="grid md:grid-cols-2 gap-6",
                        ),
                        rx.el.div(
                            rx.el.span(
                                f"Page {BrowseState.current_page} of {BrowseState.total_pages}",
                                class_name="text-sm text-gray-600",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Previous",
                                    on_click=BrowseState.prev_page,
                                    disabled=BrowseState.current_page <= 1,
                                    class_name="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50",
                                ),
                                rx.el.button(
                                    "Next",
                                    on_click=BrowseState.next_page,
                                    disabled=BrowseState.current_page
                                    >= BrowseState.total_pages,
                                    class_name="ml-2 px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50",
                                ),
                                class_name="flex",
                            ),
                            class_name="flex items-center justify-between mt-8 text-sm font-medium text-gray-700",
                        ),
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