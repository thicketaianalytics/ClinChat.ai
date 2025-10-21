import reflex as rx
from app.states.analytics_state import AnalyticsState
from app.states.ui_state import UIState
from app.components.sidebar import sidebar

TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "borderColor": "#E8E8E8",
        "borderRadius": "0.75rem",
        "boxShadow": "0px 2px 6px rgba(28, 32, 36, 0.02)",
        "fontSize": "0.875rem",
    },
    "label_style": {"color": "black", "fontWeight": "500"},
}


def chart_container(title: str, chart: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="font-semibold text-gray-800 text-lg mb-4"),
        rx.el.div(
            rx.cond(
                AnalyticsState.is_loading,
                rx.el.div(
                    rx.el.div(class_name="h-64 bg-gray-200 rounded-md animate-pulse")
                ),
                chart,
            ),
            class_name="h-80",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def phase_distribution_chart() -> rx.Component:
    return chart_container(
        "Trial Distribution by Phase",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="count", fill="#3b82f6", radius=[4, 4, 0, 0]),
            rx.recharts.x_axis(data_key="phase"),
            rx.recharts.y_axis(),
            data=AnalyticsState.phase_distribution,
        ),
    )


def status_distribution_chart() -> rx.Component:
    return chart_container(
        "Trial Distribution by Status",
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.area(
                data_key="count",
                type_="natural",
                stroke="#3b82f6",
                fill="#3b82f6",
                fill_opacity=0.3,
            ),
            rx.recharts.x_axis(data_key="status"),
            rx.recharts.y_axis(),
            data=AnalyticsState.status_distribution,
        ),
    )


def enrollment_trends_chart() -> rx.Component:
    return chart_container(
        "Enrollment Trends by Phase",
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.line(
                data_key="avg_enrollment",
                type_="monotone",
                stroke="#3b82f6",
                stroke_width=2,
                name="Average",
            ),
            rx.recharts.line(
                data_key="median_enrollment",
                type_="monotone",
                stroke="#8b5cf6",
                stroke_width=2,
                name="Median",
            ),
            rx.recharts.x_axis(data_key="phase"),
            rx.recharts.y_axis(),
            data=AnalyticsState.enrollment_trends,
        ),
    )


def geographic_distribution_chart() -> rx.Component:
    return chart_container(
        "Top 10 Countries by Trial Count",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="count", fill="#3b82f6"),
            rx.recharts.x_axis(data_key="country"),
            rx.recharts.y_axis(),
            data=AnalyticsState.geographic_distribution,
        ),
    )


def top_sponsors_chart() -> rx.Component:
    return chart_container(
        "Top 10 Sponsors by Trial Count",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="count", fill="#3b82f6"),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(width=80),
            data=AnalyticsState.sponsor_analysis,
            layout="vertical",
        ),
    )


def timeline_analysis_chart() -> rx.Component:
    return chart_container(
        "Trial Starts by Year",
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.area(
                data_key="count",
                type_="natural",
                stroke="#3b82f6",
                fill="#3b82f6",
                fill_opacity=0.3,
            ),
            rx.recharts.x_axis(data_key="year"),
            rx.recharts.y_axis(),
            data=AnalyticsState.timeline_data,
        ),
    )


def top_conditions_chart() -> rx.Component:
    return chart_container(
        "Top 10 Conditions by Trial Count",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(horizontal=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="count", fill="#3b82f6"),
            rx.recharts.x_axis(
                data_key="name", angle=-45, text_anchor="end", height=70
            ),
            rx.recharts.y_axis(),
            data=AnalyticsState.top_conditions,
        ),
    )


def top_interventions_chart() -> rx.Component:
    return chart_container(
        "Top 10 Drug Interventions by Trial Count",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(horizontal=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="count", fill="#3b82f6"),
            rx.recharts.x_axis(
                data_key="name", angle=-45, text_anchor="end", height=90
            ),
            rx.recharts.y_axis(),
            data=AnalyticsState.top_interventions,
        ),
    )


def us_state_distribution_chart() -> rx.Component:
    return chart_container(
        "Top 20 US States by Trial Count",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="count", fill="#3b82f6"),
            rx.recharts.x_axis(data_key="state"),
            rx.recharts.y_axis(),
            data=AnalyticsState.us_state_distribution,
        ),
    )


def trial_duration_chart() -> rx.Component:
    return chart_container(
        "Median Trial Duration by Phase (Days)",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(
                data_key="median_duration_days", fill="#3b82f6", radius=[4, 4, 0, 0]
            ),
            rx.recharts.x_axis(data_key="phase"),
            rx.recharts.y_axis(),
            data=AnalyticsState.trial_duration_distribution,
        ),
    )


def design_patterns_chart() -> rx.Component:
    return chart_container(
        "Trial Design Patterns (Masking)",
        rx.recharts.pie_chart(
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.pie(
                data_key="count",
                name_key="masking",
                data=AnalyticsState.design_patterns,
                cx="50%",
                cy="50%",
                outer_radius=80,
                fill="#8884d8",
                label=True,
                stroke="#fff",
                stroke_width=2,
            ),
        ),
    )


def trending_conditions_chart() -> rx.Component:
    return chart_container(
        "Top 10 Trending Conditions (Since 2020)",
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(data_key="total_trials", fill="#3b82f6"),
            rx.recharts.x_axis(data_key="name"),
            rx.recharts.y_axis(width=80),
            data=AnalyticsState.trending_conditions,
            layout="vertical",
        ),
    )


def overview_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(phase_distribution_chart(), class_name="md:col-span-1"),
        rx.el.div(status_distribution_chart(), class_name="md:col-span-1"),
        rx.el.div(enrollment_trends_chart(), class_name="md:col-span-2"),
        rx.el.div(geographic_distribution_chart(), class_name="md:col-span-1"),
        rx.el.div(top_sponsors_chart(), class_name="md:col-span-1"),
        rx.el.div(timeline_analysis_chart(), class_name="md:col-span-2"),
        rx.el.div(top_conditions_chart(), class_name="md:col-span-2"),
        rx.el.div(top_interventions_chart(), class_name="md:col-span-2"),
        class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-6",
    )


def advanced_analytics_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(us_state_distribution_chart(), class_name="md:col-span-2"),
        rx.el.div(trial_duration_chart(), class_name="md:col-span-2"),
        rx.el.div(design_patterns_chart(), class_name="md:col-span-2"),
        rx.el.div(trending_conditions_chart(), class_name="md:col-span-2"),
        class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-6",
    )


def analytics_tabs() -> rx.Component:
    tabs = ["Overview", "Advanced Analytics"]
    return rx.el.div(
        rx.el.div(
            rx.foreach(
                tabs,
                lambda tab: rx.el.button(
                    tab,
                    on_click=lambda: AnalyticsState.set_active_tab(
                        tab.lower().replace(" ", "_")
                    ),
                    class_name=rx.cond(
                        AnalyticsState.active_tab == tab.lower().replace(" ", "_"),
                        "px-4 py-2 text-sm font-semibold text-white bg-blue-600 rounded-md",
                        "px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md",
                    ),
                ),
            ),
            class_name="flex items-center gap-2 border-b border-gray-200 pb-3 mb-6",
        ),
        rx.match(
            AnalyticsState.active_tab,
            ("overview", overview_tab_content()),
            ("advanced_analytics", advanced_analytics_tab_content()),
            overview_tab_content(),
        ),
    )


def analytics_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Analytics & Insights Dashboard",
                    class_name="text-2xl font-bold text-gray-800",
                ),
                rx.el.p(
                    "Visualizing clinical trial data trends.",
                    class_name="text-gray-600",
                ),
                rx.el.button(
                    "Export Report",
                    on_click=AnalyticsState.export_analytics_report,
                    class_name="text-sm font-medium bg-white text-gray-700 border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
            analytics_tabs(),
            class_name=rx.cond(
                UIState.sidebar_collapsed,
                "p-8 flex-1 md:ml-20 transition-all duration-300",
                "p-8 flex-1 md:ml-64 transition-all duration-300",
            ),
        ),
        class_name="flex font-['DM_Sans'] bg-gray-50 min-h-screen",
    )