import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    ROUTE = "auth/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email = page.get_by_placeholder("email@example.com")
        self.password = page.get_by_placeholder("enter your passsword")  # sic: typo is in the app
        self.login_button = page.get_by_role("button", name="Login")
        self.email_required = page.get_by_text("*Email is required")
        self.password_required = page.get_by_text("*Password is required")

    @allure.step("Open login page")
    def open_page(self) -> "LoginPage":
        self.open(self.ROUTE)
        expect(self.login_button).to_be_visible()
        return self

    @allure.step("Submit login form")
    def login(self, email: str, password: str) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.login_button.click()

    def expect_validation_errors(self) -> None:
        expect(self.email_required).to_be_visible()
        expect(self.password_required).to_be_visible()

    def expect_login_rejected(self) -> None:
        self.expect_toast("Incorrect email or password.")
        expect(self.page).to_have_url(self.url(self.ROUTE))
