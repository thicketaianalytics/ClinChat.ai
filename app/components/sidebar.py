import reflex as rx
from app.states.ui_state import UIState


def nav_item(text: str, icon: str, href: str, is_active: bool) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon(tag=icon, size=20),
            rx.el.span(
                text,
                class_name=rx.cond(
                    UIState.sidebar_collapsed,
                    "absolute left-14 w-32 px-2 py-1 text-sm bg-gray-800 text-white rounded-md scale-0 group-hover:scale-100 transition-transform origin-left",
                    "ml-3 font-medium",
                ),
            ),
            class_name=rx.cond(
                UIState.sidebar_collapsed,
                "flex items-center justify-center h-10 w-10",
                "flex items-center",
            ),
        ),
        href=href,
        class_name=rx.cond(
            UIState.sidebar_collapsed,
            rx.cond(
                is_active,
                "flex items-center justify-center h-12 w-12 text-white bg-blue-600 rounded-lg group relative",
                "flex items-center justify-center h-12 w-12 text-gray-700 hover:bg-gray-100 rounded-lg group relative transition-colors",
            ),
            rx.cond(
                is_active,
                "flex items-center px-4 py-2.5 text-sm text-white bg-blue-600 rounded-lg",
                "flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors",
            ),
        ),
    )


def sidebar() -> rx.Component:
    current_path = rx.State.router.page.path
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon(tag="activity", class_name="text-blue-600", size=32),
                    rx.cond(
                        ~UIState.sidebar_collapsed,
                        rx.el.h1(
                            rx.el.span("Clin", class_name="font-bold"),
                            "Chat.ai",
                            class_name="text-xl text-gray-800 whitespace-nowrap overflow-hidden",
                        ),
                    ),
                    href="/dashboard",
                    class_name="flex items-center gap-2 overflow-hidden",
                ),
                class_name="flex items-center justify-between p-4 border-b border-gray-200 h-[69px]",
            ),
            rx.el.nav(
                nav_item(
                    "Dashboard",
                    "layout-dashboard",
                    "/dashboard",
                    current_path == "/dashboard",
                ),
                nav_item(
                    "Browse Trials", "search", "/browse", current_path == "/browse"
                ),
                nav_item(
                    "Advanced Search",
                    "search-code",
                    "/advanced-search",
                    current_path == "/advanced-search",
                ),
                nav_item(
                    "My Trials", "bookmark", "/my-trials", current_path == "/my-trials"
                ),
                nav_item(
                    "Compare Trials",
                    "git-compare-arrows",
                    "/compare",
                    current_path == "/compare",
                ),
                nav_item(
                    "Analytics",
                    "bar-chart-2",
                    "/analytics",
                    current_path == "/analytics",
                ),
                nav_item(
                    "Workspaces", "users", "/workspaces", current_path == "/workspaces"
                ),
                class_name=rx.cond(
                    UIState.sidebar_collapsed,
                    "flex-1 p-2 space-y-2",
                    "flex-1 p-4 space-y-2",
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        tag=rx.cond(
                            UIState.sidebar_collapsed, "chevrons-right", "chevrons-left"
                        ),
                        size=20,
                    ),
                    on_click=UIState.toggle_sidebar,
                    class_name="p-2 text-gray-600 hover:bg-gray-100 rounded-md w-full flex items-center justify-center",
                ),
                class_name="p-4 border-t border-gray-200",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name=rx.cond(
            UIState.sidebar_collapsed,
            "fixed top-0 left-0 w-20 bg-white border-r border-gray-200 h-screen hidden md:flex flex-col transition-all duration-300",
            "fixed top-0 left-0 w-64 bg-white border-r border-gray-200 h-screen hidden md:flex flex-col transition-all duration-300",
        ),
    )