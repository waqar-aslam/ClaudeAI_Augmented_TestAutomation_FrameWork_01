import allure
import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, allure.feature("Authentication")]


@allure.title("Valid user can log in and reach the dashboard")
@allure.description("Logging in with the practice account lands on the authenticated dashboard.")
def test_valid_user_can_login_and_see_dashboard(page, credentials):
    login = LoginPage(page).open_page()
    login.login(credentials["email"], credentials["password"])
    DashboardPage(page).expect_loaded()


@allure.title("Invalid credentials are rejected with an error")
def test_login_is_rejected_for_wrong_password(page, credentials):
    login = LoginPage(page).open_page()
    login.login(credentials["email"], "Wrong#Pass-1")
    login.expect_login_rejected()


@allure.title("Empty login form shows required-field validation")
def test_login_shows_validation_when_form_is_empty(page):
    login = LoginPage(page).open_page()
    login.login_button.click()
    login.expect_validation_errors()
