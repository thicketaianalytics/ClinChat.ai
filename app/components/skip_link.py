import reflex as rx


def skip_to_content() -> rx.Component:
    """Accessibility skip link for keyboard navigation."""
    return rx.el.a(
        "Skip to main content",
        href="#main-content",
        class_name="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-blue-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-md focus:shadow-lg",
    )