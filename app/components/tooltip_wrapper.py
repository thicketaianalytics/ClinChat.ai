import reflex as rx


def tooltip(content: str, child: rx.Component, side: str = "top") -> rx.Component:
    """Wraps a component with a tooltip using Radix Tooltip."""
    return rx.radix.tooltip(child, content=content, side=side)