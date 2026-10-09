import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_title = page.get_by_text("Payment Method")
        self.cvv = self._field("CVV Code")
        self.name_on_card = self._field("Name on Card")
        self.country = page.get_by_placeholder("Select Country")
        self.place_order_button = page.get_by_text("Place Order")

    def _field(self, title: str):
        return self.page.locator(".field").filter(has_text=title).locator("input")

    @allure.step("Fill checkout details")
    def fill_details(self, cvv: str, name_on_card: str, country: str) -> None:
        expect(self.payment_title).to_be_visible()
        self.cvv.fill(cvv)
        self.name_on_card.fill(name_on_card)
        self.country.press_sequentially(country[:3], delay=50)
        option = self.page.locator(".ta-results button").filter(has_text=re.compile(rf"^\s*{re.escape(country)}\s*$"))
        option.click()

    @allure.step("Place order")
    def place_order(self) -> None:
        self.place_order_button.click()
