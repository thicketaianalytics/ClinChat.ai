import reflex as rx
from app.states.auth_state import AuthState
from app.components.auth_layout import auth_layout


def registration_page() -> rx.Component:
    return auth_layout(
        rx.el.h2(
            "Create an Account", class_name="text-xl font-semibold text-gray-800 mb-1"
        ),
        rx.el.p(
            "Fill in the details below to create a new account.",
            class_name="text-sm text-gray-600 mb-6",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Email", class_name="text-sm font-medium text-gray-700 mb-1"
                ),
                rx.el.input(
                    placeholder="email@example.com",
                    name="email",
                    type="email",
                    class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Password", class_name="text-sm font-medium text-gray-700 mb-1"
                ),
                rx.el.input(
                    placeholder="At least 8 characters",
                    name="password",
                    type="password",
                    class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Confirm Password",
                    class_name="text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="Re-enter your password",
                    name="confirm_password",
                    type="password",
                    class_name="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                class_name="mb-4",
            ),
            rx.cond(
                AuthState.error_message != "",
                rx.el.div(
                    AuthState.error_message,
                    class_name="text-red-500 text-sm mb-4 p-2 bg-red-50 rounded-md border border-red-200",
                ),
            ),
            rx.el.button(
                "Create Account",
                type="submit",
                class_name="w-full bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors",
            ),
            on_submit=AuthState.handle_registration,
            reset_on_submit=False,
        ),
        rx.el.div(
            "Already have an account? ",
            rx.el.a(
                "Sign In",
                href="/login",
                class_name="font-medium text-blue-600 hover:underline",
            ),
            class_name="text-center mt-6 text-sm text-gray-600",
        ),
    )