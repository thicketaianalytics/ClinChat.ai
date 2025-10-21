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
    is_processing: bool = False

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

    @rx.event(background=True)
    async def handle_registration(self, form_data: dict):
        validation_passed = False
        error_message_local = ""
        async with self:
            self.is_processing = True
            if self._validate_registration(form_data):
                validation_passed = True
            else:
                error_message_local = self.error_message
                self.is_processing = False
        if not validation_passed:
            yield rx.toast.warning(error_message_local)
            return
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        password_hash = self._hash_password(password)
        new_user = User(email=email, password_hash=password_hash)
        _users[email] = new_user
        async with self:
            self.is_authenticated = True
            self.user = new_user
            self.is_processing = False
            yield rx.toast.success("Registration successful! Welcome.")
            yield rx.redirect("/dashboard")

    @rx.event(background=True)
    async def handle_login(self, form_data: dict):
        async with self:
            self.is_processing = True
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            async with self:
                self.error_message = "Email and password are required."
                self.is_processing = False
                yield rx.toast.warning(self.error_message)
            return
        user = _users.get(email)
        if user and self._verify_password(password, user["password_hash"]):
            async with self:
                self.is_authenticated = True
                self.user = user
                self.error_message = ""
                self.is_processing = False
                yield rx.toast.success("Login successful! Welcome back.")
                yield rx.redirect("/dashboard")
        else:
            async with self:
                self.error_message = "Invalid email or password."
                self.is_processing = False
                yield rx.toast.error(self.error_message)

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