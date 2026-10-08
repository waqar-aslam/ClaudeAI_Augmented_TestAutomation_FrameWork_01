import allure
from playwright.sync_api import Page


@allure.title("Verify Playwright homepage")
@allure.description("Verify that the Playwright homepage opens successfully.")
def test_open_playwright(page: Page):

    with allure.step("Open Playwright website"):
        page.goto("https://playwright.dev/")

    with allure.step("Verify page title"):
        assert page.title() == "Playwright"