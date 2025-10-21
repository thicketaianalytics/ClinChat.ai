import reflex as rx
from app.states.alerts_state import AlertsState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar


def watchlist_criteria_summary(criteria: rx.Var[dict]) -> rx.Component:
    def criterion_badge(key: str, value: rx.Var) -> rx.Component:
        return rx.cond(
            value,
            rx.el.span(
                rx.el.span(f"{key.capitalize()}: ", class_name="font-semibold"),
                value,
                class_name="text-xs font-medium bg-gray-100 text-gray-700 px-2 py-1 rounded",
            ),
        )

    return rx.el.div(
        criterion_badge("condition", criteria["condition"]),
        criterion_badge("intervention", criteria["intervention"]),
        criterion_badge("sponsor", criteria["sponsor"]),
        criterion_badge("phase", criteria["phase"]),
        criterion_badge("status", criteria["status"]),
        criterion_badge("country", criteria["country"]),
        class_name="flex flex-wrap gap-2",
    )


def watchlist_card(watchlist: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                watchlist["name"],
                class_name="text-lg font-semibold text-gray-800 truncate",
            ),
            rx.el.p(
                watchlist["description"],
                class_name="text-sm text-gray-500 h-10 overflow-hidden",
            ),
            class_name="flex-1 mb-3",
        ),
        rx.el.div(watchlist_criteria_summary(watchlist["criteria"]), class_name="mb-3"),
        rx.el.div(
            rx.el.div(
                rx.el.p("Matches", class_name="text-xs text-gray-500"),
                rx.el.p(
                    watchlist["matches"].length().to_string(),
                    class_name="text-sm font-medium text-gray-800",
                ),
            ),
            rx.el.div(
                rx.el.p("Last Checked", class_name="text-xs text-gray-500"),
                rx.el.p(
                    watchlist.get("last_checked", "Never").to_string().split("T")[0],
                    class_name="text-sm font-medium text-gray-800",
                ),
            ),
            class_name="grid grid-cols-2 gap-2 text-center border-t border-b border-gray-200 py-2",
        ),
        rx.el.div(
            rx.el.button(
                "Check Now",
                on_click=lambda: AlertsState.check_watchlist(watchlist["watchlist_id"]),
                class_name="flex-1 text-sm font-medium text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-md transition-colors",
            ),
            rx.el.a(
                "View Matches",
                href=f"/alerts/{watchlist['watchlist_id']}",
                class_name="flex-1 text-center text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded-md transition-colors",
            ),
            class_name="mt-2 flex gap-2 items-center",
        ),
        rx.el.div(
            rx.el.div(
                rx.radix.switch(
                    checked=watchlist["is_active"],
                    on_change=lambda _: AlertsState.toggle_watchlist(
                        watchlist["watchlist_id"]
                    ),
                ),
                rx.el.span("Active", class_name="text-xs font-medium text-gray-600"),
                class_name="flex items-center gap-2",
            ),
            rx.el.button(
                rx.icon(tag="trash-2", size=16),
                on_click=lambda: AlertsState.delete_watchlist(
                    watchlist["watchlist_id"]
                ),
                class_name="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors",
            ),
            class_name="mt-2 flex justify-between items-center border-t border-gray-200 pt-2",
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col h-full",
    )


def create_watchlist_dialog() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button(
                rx.icon(tag="plus", size=16, class_name="mr-2"),
                "Create New Watchlist",
                class_name="flex items-center bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
            )
        ),
        rx.radix.primitives.dialog.overlay(
            class_name="DialogOverlay fixed inset-0 bg-black/50"
        ),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Create New Watchlist", class_name="text-lg font-semibold text-gray-800"
            ),
            rx.radix.primitives.dialog.description(
                "Define criteria for trials you want to monitor.",
                class_name="text-sm text-gray-600 mt-1 mb-4",
            ),
            rx.el.form(
                rx.el.input(
                    name="name",
                    placeholder="Watchlist Name",
                    class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md mb-3",
                ),
                rx.el.textarea(
                    name="description",
                    placeholder="Description (optional)",
                    class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md mb-3",
                ),
                rx.el.div(
                    rx.el.input(
                        name="condition", placeholder="Condition (e.g., Asthma)"
                    ),
                    rx.el.input(
                        name="intervention", placeholder="Intervention (e.g., Drug X)"
                    ),
                    rx.el.input(name="sponsor", placeholder="Sponsor (e.g., Pfizer)"),
                    rx.el.input(name="phase", placeholder="Phase (e.g., PHASE2)"),
                    rx.el.input(name="status", placeholder="Status (e.g., RECRUITING)"),
                    rx.el.input(
                        name="country", placeholder="Country (e.g., United States)"
                    ),
                    class_name="grid grid-cols-2 gap-3 mb-4",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            class_name="bg-gray-100 text-gray-700 text-sm font-medium py-2 px-4 rounded-md hover:bg-gray-200",
                        )
                    ),
                    rx.el.button(
                        "Create Watchlist",
                        type="submit",
                        class_name="bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700",
                    ),
                    class_name="flex justify-end gap-3",
                ),
                on_submit=AlertsState.create_watchlist,
                reset_on_submit=True,
            ),
            class_name="DialogContent fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-lg rounded-xl bg-white p-6 shadow-lg",
        ),
        open=AlertsState.show_create_dialog,
        on_open_change=AlertsState.set_show_create_dialog,
    )


def alerts_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Alerts & Watchlists", class_name="text-2xl font-bold text-gray-800"
                ),
                rx.el.p(
                    "Proactively monitor clinical trials that match your criteria.",
                    class_name="text-gray-600",
                ),
                create_watchlist_dialog(),
                class_name="flex justify-between items-center mb-6",
            ),
            rx.cond(
                AlertsState.is_loading,
                rx.el.div(
                    rx.spinner(size="3"),
                    class_name="flex justify-center items-center h-96",
                ),
                rx.cond(
                    AlertsState.watchlists.length() > 0,
                    rx.el.div(
                        rx.foreach(AlertsState.watchlists, watchlist_card),
                        class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-6",
                    ),
                    rx.el.div(
                        rx.icon(
                            tag="bell-plus", size=48, class_name="text-gray-400 mx-auto"
                        ),
                        rx.el.h3(
                            "Create Your First Watchlist",
                            class_name="mt-4 text-lg font-semibold text-gray-800",
                        ),
                        rx.el.p(
                            "Get started by creating a watchlist to monitor new trials automatically.",
                            class_name="mt-1 text-sm text-gray-500",
                        ),
                        class_name="text-center py-16 px-6 bg-white rounded-xl border border-dashed border-gray-300 shadow-sm",
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