import reflex as rx
from app.states.ui_state import UIState


def mobile_nav_toggle() -> rx.Component:
    """Mobile hamburger menu button."""
    return rx.el.button(
        rx.icon(
            tag=rx.cond(~UIState.sidebar_collapsed, "x", "menu"),
            size=24,
            class_name="text-gray-700",
        ),
        on_click=UIState.toggle_sidebar,
        class_name="md:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors",
        aria_label="Toggle navigation menu",
    )


def mobile_sidebar_overlay() -> rx.Component:
    """Overlay that appears when sidebar is open on mobile."""
    return rx.cond(
        ~UIState.sidebar_collapsed,
        rx.el.div(
            on_click=UIState.toggle_sidebar,
            class_name="md:hidden fixed inset-0 bg-black bg-opacity-50 z-30",
            aria_hidden="true",
        ),
    )