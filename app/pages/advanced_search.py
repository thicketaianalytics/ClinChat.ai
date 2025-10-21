import reflex as rx
from app.states.advanced_search_state import AdvancedSearchState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar
from app.pages.browse import trial_card


def natural_language_search_box() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Natural Language Query",
            class_name="text-lg font-semibold text-gray-800 mb-2",
        ),
        rx.el.p(
            "Use everyday language to search for trials. Try one of the examples below.",
            class_name="text-sm text-gray-600 mb-4",
        ),
        rx.el.form(
            rx.el.input(
                name="natural_query",
                placeholder="e.g., Phase 3 trials on Alzheimer's since 2020 with Biogen as sponsor",
                class_name="w-full text-sm border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
                default_value=AdvancedSearchState.natural_query,
            ),
            rx.el.button(
                "Search",
                type="submit",
                class_name="bg-blue-600 text-white font-medium py-2 px-6 rounded-md hover:bg-blue-700",
            ),
            on_submit=AdvancedSearchState.handle_natural_query_submit,
            class_name="flex items-center gap-2",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
    )


def query_builder() -> rx.Component:
    def query_input(name: str, placeholder: str, label: str) -> rx.Component:
        return rx.el.div(
            rx.el.label(label, class_name="text-xs font-medium text-gray-600 mb-1"),
            rx.el.input(
                name=name,
                placeholder=placeholder,
                default_value=AdvancedSearchState.structured_query[name],
                class_name="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500",
            ),
        )

    return rx.el.div(
        rx.el.h2(
            "Advanced Query Builder",
            class_name="text-lg font-semibold text-gray-800 mb-4",
        ),
        rx.el.form(
            rx.el.div(
                query_input("condition", "e.g., Alzheimer's Disease", "Condition"),
                query_input("intervention", "e.g., Lecanemab", "Intervention"),
                query_input("sponsor", "e.g., Biogen", "Sponsor"),
                query_input("status", "e.g., Recruiting", "Status"),
                query_input("phase", "e.g., Phase 3", "Phase"),
                class_name="grid md:grid-cols-3 lg:grid-cols-5 gap-4",
            ),
            rx.el.div(
                query_input("min_enrollment", "e.g., 100", "Min Enrollment"),
                query_input("max_enrollment", "e.g., 500", "Max Enrollment"),
                query_input("start_date_from", "YYYY-MM-DD", "Start Date From"),
                query_input("start_date_to", "YYYY-MM-DD", "Start Date To"),
                class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4",
            ),
            rx.el.div(
                rx.el.button(
                    "Build & Search",
                    type="submit",
                    class_name="bg-blue-600 text-white font-medium py-2 px-6 rounded-md hover:bg-blue-700",
                ),
                class_name="flex justify-end mt-4",
            ),
            on_submit=AdvancedSearchState.handle_structured_query_submit,
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
    )


def side_panel() -> rx.Component:
    def history_item(query: rx.Var[dict]) -> rx.Component:
        return rx.el.button(
            rx.el.p(
                query["natural_query"], class_name="text-sm text-gray-700 truncate"
            ),
            rx.el.p(
                str(query["timestamp"]).split("T")[0],
                class_name="text-xs text-gray-500",
            ),
            on_click=lambda: AdvancedSearchState.load_from_history(query),
            class_name="w-full text-left p-2 rounded-md hover:bg-gray-100",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Query History", class_name="text-base font-semibold text-gray-800 mb-2"
            ),
            rx.el.div(
                rx.foreach(AdvancedSearchState.query_history, history_item),
                class_name="space-y-1",
            ),
            class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-4",
        ),
        rx.el.div(
            rx.el.h3(
                "Saved Searches",
                class_name="text-base font-semibold text-gray-800 mb-2",
            ),
            class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="lg:col-span-1",
    )


def search_results() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                f"Search Results ({AdvancedSearchState.total_results} found)",
                class_name="text-lg font-semibold text-gray-800",
            ),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.cond(
            AdvancedSearchState.is_searching,
            rx.el.div(
                rx.spinner(size="3"), class_name="flex items-center justify-center h-64"
            ),
            rx.el.div(
                rx.foreach(AdvancedSearchState.search_results, trial_card),
                class_name="grid md:grid-cols-2 gap-6",
            ),
        ),
        class_name="lg:col-span-3",
    )


def advanced_search_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Advanced Search", class_name="text-2xl font-bold text-gray-800"
                ),
                rx.el.p(
                    "Construct complex queries using natural language or the query builder.",
                    class_name="text-gray-600",
                ),
                class_name="mb-6",
            ),
            natural_language_search_box(),
            query_builder(),
            rx.el.div(
                search_results(), side_panel(), class_name="grid lg:grid-cols-4 gap-6"
            ),
            class_name=rx.cond(
                UIState.sidebar_collapsed,
                "p-8 flex-1 md:ml-20 transition-all duration-300",
                "p-8 flex-1 md:ml-64 transition-all duration-300",
            ),
        ),
        class_name="flex font-['DM_Sans'] bg-gray-50 min-h-screen",
    )