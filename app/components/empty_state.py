import reflex as rx


def empty_state(
    icon: str,
    title: str,
    description: str,
    button_text: str | None = None,
    button_action: rx.event.EventHandler | None = None,
    href: str | None = None,
) -> rx.Component:
    """A reusable component for displaying empty states."""
    action_button = rx.cond(
        button_text,
        rx.el.a(
            button_text,
            href=href,
            on_click=button_action,
            class_name="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700",
        ),
    )
    return rx.el.div(
        rx.icon(tag=icon, size=48, class_name="text-gray-400 mx-auto"),
        rx.el.h3(title, class_name="mt-4 text-lg font-semibold text-gray-800"),
        rx.el.p(description, class_name="mt-1 text-sm text-gray-500"),
        action_button,
        class_name="text-center py-16 px-6 bg-white rounded-xl border border-dashed border-gray-300 shadow-sm",
    )