import reflex as rx


class UIState(rx.State):
    sidebar_collapsed: bool = True
    filters_collapsed: bool = False

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed

    @rx.event
    def toggle_filters(self):
        self.filters_collapsed = not self.filters_collapsed