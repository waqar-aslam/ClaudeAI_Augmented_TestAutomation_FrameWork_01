from playwright.sync_api import Page, expect

from config.settings import settings


class BasePage:
    """Shared helpers. Subclasses own their locators and interactions."""

    def __init__(self, page: Page):
        self.page = page
        self.toast = page.locator("#toast-container")

    @staticmethod
    def url(route: str) -> str:
        return f"{settings.base_url}/#/{route.lstrip('/')}"

    def open(self, route: str) -> None:
        self.page.goto(self.url(route))

    def expect_toast(self, text: str) -> None:
        expect(self.toast).to_contain_text(text)
