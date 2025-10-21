import reflex as rx


def skeleton_text(class_name: str) -> rx.Component:
    """A simple skeleton loader for text."""
    return rx.el.div(class_name=f"bg-gray-200 rounded animate-pulse {class_name}")


def metric_card_skeleton() -> rx.Component:
    """A skeleton loader for a metric card."""
    return rx.el.div(
        rx.el.div(class_name="p-2 bg-gray-200 rounded-md w-10 h-10 animate-pulse"),
        skeleton_text(class_name="h-4 w-20 mt-2"),
        skeleton_text(class_name="h-8 w-16 mt-1"),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm animate-pulse",
    )


def trial_card_skeleton() -> rx.Component:
    """A skeleton loader that mimics the structure of a trial card."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                skeleton_text(class_name="h-4 w-24"),
                skeleton_text(class_name="h-5 w-20"),
                class_name="flex justify-between items-center mb-2",
            ),
            skeleton_text(class_name="h-5 w-full mt-2"),
            skeleton_text(class_name="h-5 w-3/4 mt-1"),
            skeleton_text(class_name="h-4 w-1/3 mt-3"),
            class_name="flex-1 mb-3",
        ),
        rx.el.div(
            rx.el.div(skeleton_text(class_name="h-8 w-full")),
            rx.el.div(skeleton_text(class_name="h-8 w-full")),
            rx.el.div(skeleton_text(class_name="h-8 w-full")),
            rx.el.div(skeleton_text(class_name="h-8 w-full")),
            class_name="grid grid-cols-2 gap-y-3 gap-x-2 text-center border-t border-b border-gray-200 py-3",
        ),
        rx.el.div(
            skeleton_text(class_name="h-9 w-full"),
            class_name="mt-2 flex justify-between items-center",
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col h-full animate-pulse",
    )