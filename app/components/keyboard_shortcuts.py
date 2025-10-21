import reflex as rx


class KeyboardShortcutsState(rx.State):
    """State for managing keyboard shortcuts."""

    show_search: bool = False

    @rx.event
    def toggle_search(self):
        self.show_search = not self.show_search

    @rx.event
    def handle_save_shortcut(self):
        return rx.toast.info("Save shortcut triggered")


def keyboard_shortcuts() -> rx.Component:
    """Global keyboard shortcuts handler."""
    return rx.fragment(
        rx.script("""
            document.addEventListener('keydown', function(e) {
                // Cmd+K or Ctrl+K - Open search
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    window.location.href = '/browse';
                }

                // Cmd+S or Ctrl+S - Save (if on detail page)
                if ((e.metaKey || e.ctrlKey) && e.key === 's') {
                    e.preventDefault();
                    // Dispatch custom event that pages can listen to
                    window.dispatchEvent(new CustomEvent('keyboard-save'));
                }

                // Escape - Close modals/dialogs
                if (e.key === 'Escape') {
                    // Radix dialogs handle this automatically
                }
            });
        """)
    )