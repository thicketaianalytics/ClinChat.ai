import reflex as rx
import bcrypt
import re
from typing import Optional
from app.models.user import User

_users: dict[str, User] = {}


class AuthState(rx.State):
    error_message: str = ""
    is_authenticated: bool = False
    user: Optional[User] = None
    is_hydrated: bool = False

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def _validate_registration(self, form_data: dict) -> bool:
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        if not email or not password or (not confirm_password):
            self.error_message = "All fields are required."
            return False
        if not re.match("[^@]+@[^@]+\\.[^@]+", email):
            self.error_message = "Invalid email address."
            return False
        if len(password) < 8:
            self.error_message = "Password must be at least 8 characters long."
            return False
        if password != confirm_password:
            self.error_message = "Passwords do not match."
            return False
        if email in _users:
            self.error_message = "An account with this email already exists."
            return False
        self.error_message = ""
        return True

    @rx.event
    def handle_registration(self, form_data: dict):
        if not self._validate_registration(form_data):
            return
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        password_hash = self._hash_password(password)
        new_user = User(email=email, password_hash=password_hash)
        _users[email] = new_user
        self.is_authenticated = True
        self.user = new_user
        return rx.redirect("/dashboard")

    @rx.event
    def handle_login(self, form_data: dict):
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.error_message = "Email and password are required."
            return
        user = _users.get(email)
        if user and self._verify_password(password, user["password_hash"]):
            self.is_authenticated = True
            self.user = user
            self.error_message = ""
            return rx.redirect("/dashboard")
        else:
            self.error_message = "Invalid email or password."

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.user = None
        self.error_message = ""
        return rx.redirect("/login")

    @rx.event
    def check_login(self):
        self.is_hydrated = True
        current_page = self.router.page.path
        if not self.is_authenticated:
            if current_page not in ["/login", "/register", "/"]:
                return rx.redirect("/login")
        elif current_page in ["/login", "/register", "/"]:
            return rx.redirect("/dashboard")