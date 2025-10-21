import reflex as rx


def hydration_fallback() -> rx.Component:
    """A fallback component displayed during app hydration."""
    return rx.el.div(
        rx.el.div(
            rx.icon(tag="activity", class_name="text-blue-600", size=48),
            rx.el.h1(
                rx.el.span("Clin", class_name="font-bold"),
                "Chat.ai",
                class_name="text-3xl text-gray-800 mt-4",
            ),
            rx.el.div(
                rx.el.div(
                    class_name="h-1.5 w-32 bg-gray-200 rounded-full overflow-hidden"
                ),
                class_name="animate-pulse mt-6",
            ),
            rx.el.p(
                "Connecting to Clinical Data Universe...",
                class_name="text-sm text-gray-500 mt-2",
            ),
            class_name="flex flex-col items-center justify-center",
        ),
        class_name="fixed inset-0 flex items-center justify-center bg-gray-50 font-['DM_Sans'] z-50",
    )