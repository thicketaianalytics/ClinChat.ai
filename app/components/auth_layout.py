import reflex as rx


def auth_layout(*args) -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon(tag="activity", class_name="text-blue-600", size=32),
                    rx.el.h1(
                        rx.el.span("Clin", class_name="font-bold"),
                        "Chat.ai",
                        class_name="text-2xl text-gray-800",
                    ),
                    href="/",
                    class_name="flex items-center gap-2 mb-8 transform hover:scale-105 transition-transform",
                ),
                *args,
                class_name="w-full max-w-md bg-white p-8 rounded-xl border border-gray-200 shadow-sm fade-in-content",
            ),
            class_name="min-h-screen w-full flex items-center justify-center bg-gray-50 font-['DM_Sans'] p-4",
        ),
        class_name="font-['DM_Sans'] bg-white",
    )