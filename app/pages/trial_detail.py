import reflex as rx
import reflex_enterprise as rxe
from app.states.trial_detail_state import TrialDetailState
from app.components.sidebar import sidebar
from app.states.ui_state import UIState
from app.states.saved_trials_state import SavedTrialsState
from app.states.report_state import ReportState
from app.components.tooltip_wrapper import tooltip
from app.states.ai_state import AIState


def detail_section(title: str, content: rx.Var, is_html: bool = True) -> rx.Component:
    return rx.cond(
        content,
        rx.el.div(
            rx.el.h3(title, class_name="font-semibold text-gray-800 text-base mb-1"),
            rx.cond(
                is_html,
                rx.el.div(
                    rx.html(
                        content.to_string().replace('"', "").replace('""', "<br />")
                    ),
                    class_name="text-sm text-gray-600 prose prose-sm max-w-none",
                ),
                rx.el.div(content, class_name="text-sm text-gray-600"),
            ),
            class_name="py-3 border-t border-gray-200",
        ),
    )


def list_section(
    title: str, items: rx.Var[list], item_component: callable
) -> rx.Component:
    return rx.cond(
        items.length() > 0,
        rx.el.div(
            rx.el.h3(title, class_name="font-semibold text-gray-800 text-base mb-2"),
            rx.el.div(rx.foreach(items, item_component), class_name="space-y-2"),
            class_name="py-3 border-t border-gray-200",
        ),
    )


def trial_infographic() -> rx.Component:
    trial = TrialDetailState.trial
    return rx.el.div(
        rx.el.div(
            rx.icon(tag="calendar-days", size=20, class_name="text-gray-500"),
            rx.el.p("Duration", class_name="text-xs text-gray-500"),
            rx.el.p(
                f"{TrialDetailState.trial_duration_days} days",
                class_name="text-sm font-medium text-gray-800",
            ),
            class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-gray-50 text-center",
        ),
        rx.el.div(
            rx.icon(tag="map_pin", size=20, class_name="text-gray-500"),
            rx.el.p("Sites", class_name="text-xs text-gray-500"),
            rx.el.p(
                trial.get("locations", []).length().to_string(),
                class_name="text-sm font-medium text-gray-800",
            ),
            class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-gray-50 text-center",
        ),
        rx.el.div(
            rx.icon(tag="users", size=20, class_name="text-gray-500"),
            rx.el.p("Participants", class_name="text-xs text-gray-500"),
            rx.el.p(
                trial.get("enrollment", "N/A"),
                class_name="text-sm font-medium text-gray-800",
            ),
            class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-gray-50 text-center",
        ),
        rx.el.div(
            rx.icon(tag="beaker", size=20, class_name="text-gray-500"),
            rx.el.p("Phase", class_name="text-xs text-gray-500"),
            rx.el.p(
                trial.get("phase", "N/A"),
                class_name="text-sm font-medium text-gray-800",
            ),
            class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-gray-50 text-center",
        ),
        rx.el.div(
            rx.icon(tag="flag", size=20, class_name="text-gray-500"),
            rx.el.p("Status", class_name="text-xs text-gray-500"),
            rx.el.span(
                trial.get("overall_status", "N/A"),
                class_name=rx.cond(
                    trial["overall_status"] == "RECRUITING",
                    "text-sm font-medium text-green-700",
                    rx.cond(
                        trial["overall_status"] == "COMPLETED",
                        "text-sm font-medium text-blue-700",
                        "text-sm font-medium text-gray-700",
                    ),
                ),
            ),
            class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-gray-50 text-center",
        ),
        complexity_badge(),
        class_name="grid grid-cols-3 md:grid-cols-6 gap-2 py-3 border-t border-b border-gray-200",
    )


def complexity_badge() -> rx.Component:
    rating = TrialDetailState.complexity_rating
    color_class = rx.match(
        rating,
        ("Low", "bg-green-100 text-green-800"),
        ("Medium", "bg-yellow-100 text-yellow-800"),
        ("High", "bg-orange-100 text-orange-800"),
        ("Very High", "bg-red-100 text-red-800"),
        "bg-gray-100 text-gray-800",
    )
    return tooltip(
        f"Score based on number of locations, interventions, outcomes, etc. Total: {TrialDetailState.complexity_score} points.",
        rx.el.div(
            rx.icon(tag="puzzle", size=20, class_name="text-gray-500"),
            rx.el.p("Complexity", class_name="text-xs text-gray-500"),
            rx.el.span(
                rating,
                class_name=f"text-sm font-medium {color_class} px-2 py-0.5 rounded-full",
            ),
            class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-gray-50 text-center",
        ),
    )


def enrollment_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Enrollment", class_name="font-semibold text-gray-800 text-base mb-2"),
        rx.el.div(
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
                rx.recharts.x_axis(data_key="name", type_="category"),
                rx.recharts.y_axis(type_="number"),
                rx.recharts.bar(data_key="value", fill="#3b82f6", radius=[4, 4, 0, 0]),
                data=[
                    {
                        "name": "Actual Enrollment",
                        "value": TrialDetailState.trial.get("enrollment", 0),
                    }
                ],
                height=200,
            )
        ),
        class_name="py-3 border-t border-gray-200",
    )


def trial_locations_map() -> rx.Component:
    return rx.cond(
        TrialDetailState.location_markers.length() > 0,
        rx.el.div(
            rx.el.h3(
                "Geographic Locations",
                class_name="font-semibold text-gray-800 text-base mb-2",
            ),
            rxe.map(
                rxe.map.tile_layer(
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                ),
                rx.foreach(
                    TrialDetailState.location_markers,
                    lambda marker: rxe.map.marker(
                        rxe.map.popup(rx.html(marker["popup"])),
                        position=marker["position"],
                    ),
                ),
                id="trial-detail-map",
                center=TrialDetailState.map_center,
                zoom=TrialDetailState.map_zoom,
                height="400px",
                width="100%",
                class_name="rounded-lg",
            ),
            class_name="py-3 border-t border-gray-200",
        ),
    )


def sponsor_portfolio_section() -> rx.Component:
    return rx.cond(
        (TrialDetailState.sponsor_portfolio.length() > 0)
        & TrialDetailState.lead_sponsor,
        rx.el.div(
            rx.el.h3(
                f"More from {TrialDetailState.lead_sponsor.get('name', 'Sponsor')}",
                class_name="font-semibold text-gray-800 text-base mb-2",
            ),
            rx.el.div(
                rx.foreach(
                    TrialDetailState.sponsor_portfolio,
                    lambda trial: rx.el.a(
                        rx.el.p(
                            trial["brief_title"],
                            class_name="text-sm font-medium text-blue-600 hover:underline truncate",
                        ),
                        rx.el.p(
                            f"NCT: {trial['nct_id']} | Phase: {trial['phase']} | Status: {trial['overall_status']}",
                            class_name="text-xs text-gray-500",
                        ),
                        href=f"/trial/{trial['nct_id']}",
                        class_name="block p-2 rounded-md hover:bg-gray-50",
                    ),
                ),
                class_name="space-y-1",
            ),
            class_name="py-3 border-t border-gray-200",
        ),
    )


def similar_trial_card(trial: rx.Var[dict]) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.p(
                trial["brief_title"],
                class_name="text-sm font-medium text-gray-800 truncate text-left",
            ),
            rx.el.p(
                f"NCT ID: {trial['nct_id']}",
                class_name="text-xs text-gray-500 text-left",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.div(
            rx.el.span(
                trial["overall_status"],
                class_name=rx.cond(
                    trial["overall_status"] == "RECRUITING",
                    "text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded-full",
                    "text-xs font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded-full",
                ),
            ),
            class_name="ml-2",
        ),
        href=f"/trial/{trial['nct_id']}",
        class_name="flex items-center justify-between w-full p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors",
    )


def location_item(loc: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.p(loc.get("facility", "N/A"), class_name="font-medium text-sm"),
        rx.el.p(
            f"{loc.get('city', '')}, {loc.get('state', '')} {loc.get('zip', '')}, {loc.get('country', '')}".strip(
                ", "
            ),
            class_name="text-xs text-gray-600",
        ),
        rx.el.span(
            loc.get("status", ""),
            class_name=rx.cond(
                loc.get("status") == "Recruiting",
                "text-xs font-medium text-green-600",
                "text-xs font-medium text-gray-500",
            ),
        ),
        class_name="p-3 border rounded-lg bg-white flex justify-between items-center",
    )


def design_group_item(group: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.p(group.get("title", "N/A"), class_name="font-medium text-sm"),
        rx.el.p(
            group.get("group_type", ""),
            class_name="text-xs text-gray-500 capitalize mb-0.5",
        ),
        rx.el.p(group.get("description", ""), class_name="text-xs text-gray-600"),
        class_name="p-2 border rounded-lg bg-white",
    )


def design_outcome_item(outcome: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.p(outcome.get("measure", "N/A"), class_name="font-medium text-sm"),
        rx.el.p(
            f"Timeframe: {outcome.get('time_frame', '')}",
            class_name="text-xs text-gray-500 mb-0.5",
        ),
        rx.el.p(outcome.get("description", ""), class_name="text-xs text-gray-600"),
        class_name="p-2 border rounded-lg bg-white",
    )


def eligibility_criteria_section() -> rx.Component:
    return rx.cond(
        TrialDetailState.trial.get("eligibility_criteria"),
        rx.el.div(
            rx.el.h3(
                "Eligibility Criteria",
                class_name="font-semibold text-gray-800 text-base mb-2",
            ),
            rx.cond(
                (TrialDetailState.inclusion_criteria.length() > 0)
                | (TrialDetailState.exclusion_criteria.length() > 0),
                rx.el.div(
                    rx.cond(
                        TrialDetailState.inclusion_criteria.length() > 0,
                        rx.el.div(
                            rx.el.h4(
                                "Inclusion Criteria",
                                class_name="flex items-center text-sm font-semibold text-green-800 mb-2",
                            ),
                            rx.el.ul(
                                rx.foreach(
                                    TrialDetailState.inclusion_criteria,
                                    lambda item: rx.el.li(
                                        rx.icon(
                                            tag="square-check",
                                            class_name="h-4 w-4 text-green-500 mr-3 flex-shrink-0",
                                        ),
                                        rx.el.span(
                                            item, class_name="text-sm text-gray-700"
                                        ),
                                        class_name="flex items-start mb-2",
                                    ),
                                ),
                                class_name="list-none pl-0",
                            ),
                        ),
                    ),
                    rx.cond(
                        TrialDetailState.exclusion_criteria.length() > 0,
                        rx.el.div(
                            rx.el.h4(
                                "Exclusion Criteria",
                                class_name="flex items-center text-sm font-semibold text-red-800 mt-4 mb-2",
                            ),
                            rx.el.ul(
                                rx.foreach(
                                    TrialDetailState.exclusion_criteria,
                                    lambda item: rx.el.li(
                                        rx.icon(
                                            tag="circle-x",
                                            class_name="h-4 w-4 text-red-500 mr-3 flex-shrink-0",
                                        ),
                                        rx.el.span(
                                            item, class_name="text-sm text-gray-700"
                                        ),
                                        class_name="flex items-start mb-2",
                                    ),
                                ),
                                class_name="list-none pl-0",
                            ),
                        ),
                    ),
                    rx.cond(
                        TrialDetailState.eligibility_note != "",
                        rx.el.p(
                            rx.icon(
                                tag="info", class_name="h-4 w-4 mr-2 flex-shrink-0"
                            ),
                            TrialDetailState.eligibility_note,
                            class_name="mt-4 text-xs text-gray-600 bg-gray-50 p-2 rounded-md flex items-center",
                        ),
                    ),
                    class_name="p-3 bg-white border border-gray-200 rounded-lg",
                ),
                detail_section(
                    "", TrialDetailState.trial.get("eligibility_criteria"), is_html=True
                ),
            ),
            class_name="py-3 border-t border-gray-200",
        ),
    )


def trial_detail_page() -> rx.Component:
    trial = TrialDetailState.trial
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.a(
                            "< Back to Browse",
                            href="/browse",
                            class_name="text-sm font-medium text-blue-600 hover:underline mb-2 inline-block",
                        ),
                        rx.el.div(
                            tooltip(
                                "Save this trial to your list (Cmd+S)",
                                rx.el.button(
                                    rx.icon(tag="bookmark", size=16, class_name="mr-2"),
                                    "Save to My Trials",
                                    on_click=lambda: SavedTrialsState.save_trial(
                                        trial.get("nct_id")
                                    ),
                                    class_name="flex items-center bg-blue-600 text-white text-sm font-medium py-1.5 px-3 rounded-md hover:bg-blue-700 transition-colors",
                                    id="save-trial-button",
                                ),
                            ),
                            tooltip(
                                "Generate and download a PDF report for this trial",
                                rx.el.button(
                                    rx.icon(
                                        tag="file-down", size=16, class_name="mr-2"
                                    ),
                                    "Download PDF",
                                    on_click=ReportState.generate_trial_pdf,
                                    is_loading=ReportState.is_generating_pdf,
                                    class_name="flex items-center bg-white text-gray-700 border border-gray-300 text-sm font-medium py-1.5 px-3 rounded-md hover:bg-gray-50 transition-colors",
                                ),
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        class_name="flex items-center justify-between mb-2",
                    ),
                    rx.script("""
                        function handleSave() {
                            const saveButton = document.getElementById('save-trial-button');
                            if (saveButton) {
                                saveButton.click();
                            }
                        }
                        document.addEventListener('keyboard-save', handleSave);
                        // Clean up listener when component unmounts is handled by framework
                        """),
                    rx.cond(
                        TrialDetailState.is_loading,
                        rx.el.div(
                            rx.el.div(
                                class_name="h-8 w-3/4 bg-gray-200 rounded animate-pulse mb-2"
                            ),
                            rx.el.div(
                                class_name="h-4 w-1/4 bg-gray-200 rounded animate-pulse mb-3"
                            ),
                            rx.el.div(
                                *[
                                    rx.el.div(
                                        class_name="h-24 bg-gray-200 rounded animate-pulse"
                                    )
                                    for _ in range(4)
                                ],
                                class_name="space-y-4",
                            ),
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.h1(
                                    trial.get("brief_title", "Trial Details"),
                                    class_name="text-2xl font-bold text-gray-800",
                                ),
                                rx.el.p(
                                    f"NCT ID: {trial.get('nct_id', 'N/A')}",
                                    class_name="text-gray-600 mt-1",
                                ),
                                class_name="mb-2",
                            ),
                            trial_infographic(),
                            detail_section(
                                "Official Title", trial.get("official_title")
                            ),
                            detail_section("Brief Summary", trial.get("brief_summary")),
                            detail_section(
                                "Detailed Description",
                                trial.get("detailed_description"),
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.h3(
                                        "AI Summary",
                                        class_name="font-semibold text-gray-800 text-base",
                                    ),
                                    rx.el.button(
                                        rx.icon(
                                            tag="sparkles", size=14, class_name="mr-1.5"
                                        ),
                                        "Generate Summary",
                                        on_click=lambda: AIState.generate_trial_summary(
                                            trial["nct_id"]
                                        ),
                                        is_loading=AIState.is_generating_summary.contains(
                                            trial["nct_id"]
                                        ),
                                        class_name="flex items-center text-xs font-medium bg-purple-100 text-purple-700 px-2.5 py-1 rounded-md hover:bg-purple-200",
                                    ),
                                    class_name="flex justify-between items-center mb-2",
                                ),
                                rx.cond(
                                    AIState.is_generating_summary.contains(
                                        trial["nct_id"]
                                    ),
                                    rx.el.div(
                                        rx.spinner(),
                                        class_name="w-full flex justify-center p-4",
                                    ),
                                    rx.cond(
                                        AIState.ai_summaries.contains(trial["nct_id"]),
                                        rx.el.div(
                                            rx.html(
                                                AIState.ai_summaries[
                                                    trial["nct_id"]
                                                ].replace(
                                                    """
""",
                                                    "<br />",
                                                )
                                            ),
                                            class_name="prose prose-sm max-w-none p-3 bg-gray-50 rounded-lg border border-gray-200",
                                        ),
                                        rx.el.div(
                                            "Click button to generate an AI-powered summary.",
                                            class_name="text-center text-sm text-gray-500 p-4 border border-dashed rounded-lg",
                                        ),
                                    ),
                                ),
                                rx.el.p(
                                    f"Powered by {AIState.current_provider}",
                                    class_name="text-xs text-gray-400 text-right mt-1",
                                ),
                                class_name="py-3 border-t border-gray-200",
                            ),
                            eligibility_criteria_section(),
                            enrollment_chart(),
                            trial_locations_map(),
                            list_section(
                                "Recruiting Locations",
                                trial.get("locations", []),
                                location_item,
                            ),
                            list_section(
                                "Treatment Arms / Design Groups",
                                trial.get("design_groups", []),
                                design_group_item,
                            ),
                            list_section(
                                "Primary Outcomes",
                                TrialDetailState.primary_outcomes,
                                design_outcome_item,
                            ),
                            list_section(
                                "Secondary Outcomes",
                                TrialDetailState.secondary_outcomes,
                                design_outcome_item,
                            ),
                            list_section(
                                "Interventions",
                                trial.get("interventions", []),
                                lambda i: rx.el.div(
                                    f"{i.get('intervention_type')}: {i.get('name')}",
                                    class_name="p-3 border rounded-lg bg-white text-sm",
                                ),
                            ),
                            list_section(
                                "Sponsors",
                                trial.get("sponsors", []),
                                lambda s: rx.el.div(
                                    f"{s.get('lead_or_collaborator')}: {s.get('name')} ({s.get('agency_class')})",
                                    class_name="p-3 border rounded-lg bg-white text-sm",
                                ),
                            ),
                            sponsor_portfolio_section(),
                            rx.cond(
                                trial.get("mesh_terms", []).length() > 0,
                                rx.el.div(
                                    rx.el.h3(
                                        "Therapeutic Areas (MeSH Terms)",
                                        class_name="font-semibold text-gray-800 text-base mb-1",
                                    ),
                                    rx.el.div(
                                        rx.foreach(
                                            trial.get("mesh_terms", []),
                                            lambda term: rx.el.span(
                                                term,
                                                class_name="bg-blue-100 text-blue-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full",
                                            ),
                                        ),
                                        class_name="flex flex-wrap gap-2",
                                    ),
                                    class_name="py-3 border-t border-gray-200",
                                ),
                            ),
                            list_section(
                                "References",
                                trial.get("references", []),
                                lambda r: rx.el.div(
                                    r.get("citation"),
                                    class_name="text-xs italic text-gray-600",
                                ),
                            ),
                            rx.el.div(
                                rx.el.h2(
                                    "Similar Trials",
                                    class_name="text-xl font-semibold text-gray-800 mb-2 mt-6",
                                ),
                                rx.cond(
                                    TrialDetailState.similar_trials.length() > 0,
                                    rx.el.div(
                                        rx.foreach(
                                            TrialDetailState.similar_trials,
                                            similar_trial_card,
                                        ),
                                        class_name="space-y-2",
                                    ),
                                    rx.el.p(
                                        "No similar trials found.",
                                        class_name="text-sm text-gray-500 italic",
                                    ),
                                ),
                                class_name="py-3 border-t border-gray-200",
                            ),
                        ),
                    ),
                ),
                class_name="max-w-6xl mx-auto",
            ),
            id="main-content",
            class_name=rx.cond(
                UIState.sidebar_collapsed,
                "p-3 md:p-4 flex-1 md:ml-20 transition-all duration-300 fade-in-content",
                "p-3 md:p-4 flex-1 md:ml-64 transition-all duration-300 fade-in-content",
            ),
        ),
        class_name="flex font-['DM_Sans'] bg-gray-50 min-h-screen",
    )