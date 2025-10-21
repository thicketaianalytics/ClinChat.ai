import reflex as rx
import reflex_enterprise as rxe
from contextlib import asynccontextmanager
from app.states.auth_state import AuthState
from app.pages.login import login_page
from app.pages.register import registration_page
from app.pages.dashboard import dashboard_page
from app.pages.browse import browse_page


@asynccontextmanager
async def database_lifespan():
    """Initialize database connection pool at startup and clean up at shutdown."""
    from app.utils.db import initialize_connection_pool, close_connection_pool

    initialize_connection_pool()
    print("✅ Database connection pool initialized")
    yield
    close_connection_pool()
    print("✅ Database connection pool closed")


def index() -> rx.Component:
    from app.components.hydration_fallback import hydration_fallback

    return rx.fragment(
        rx.cond(
            AuthState.is_hydrated,
            rx.cond(AuthState.is_authenticated, dashboard_page(), login_page()),
            hydration_fallback(),
        )
    )


app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
            integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=",
            cross_origin="",
        ),
    ],
)
app.register_lifespan_task(database_lifespan)
app.add_page(index, on_load=AuthState.check_login)
app.add_page(login_page, route="/login", on_load=AuthState.check_login)
app.add_page(registration_page, route="/register", on_load=AuthState.check_login)
from app.states.dashboard_state import DashboardState
from app.states.browse_state import BrowseState
from app.states.ui_state import UIState

app.add_page(
    dashboard_page,
    route="/dashboard",
    on_load=[AuthState.check_login, DashboardState.load_dashboard_data],
)
app.add_page(
    browse_page,
    route="/browse",
    on_load=[AuthState.check_login, BrowseState.load_browse_page_data],
)
from app.pages.advanced_search import advanced_search_page
from app.states.advanced_search_state import AdvancedSearchState

app.add_page(
    advanced_search_page,
    route="/advanced-search",
    on_load=[AuthState.check_login, AdvancedSearchState.on_page_load],
)
from app.pages.my_trials import my_trials_page
from app.states.saved_trials_state import SavedTrialsState

app.add_page(
    my_trials_page,
    route="/my-trials",
    on_load=[AuthState.check_login, SavedTrialsState.load_saved_trials],
)
from app.pages.compare import compare_page
from app.states.comparison_state import ComparisonState

app.add_page(
    compare_page,
    route="/compare",
    on_load=[AuthState.check_login, ComparisonState.load_comparison_data],
)
from app.pages.trial_detail import trial_detail_page
from app.states.trial_detail_state import TrialDetailState

app.add_page(
    trial_detail_page,
    route="/trial/[nct_id]",
    on_load=[AuthState.check_login, TrialDetailState.load_trial_details],
)
from app.pages.analytics import analytics_page
from app.states.analytics_state import AnalyticsState

app.add_page(
    analytics_page,
    route="/analytics",
    on_load=[AuthState.check_login, AnalyticsState.load_analytics_data],
)
from app.pages.workspaces import workspaces_page
from app.states.workspace_state import WorkspaceState

app.add_page(
    workspaces_page,
    route="/workspaces",
    on_load=[AuthState.check_login, WorkspaceState.load_workspaces],
)