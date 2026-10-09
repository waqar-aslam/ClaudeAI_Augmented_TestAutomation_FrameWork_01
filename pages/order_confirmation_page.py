import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage

ORDER_ID = re.compile(r"[0-9a-f]{24}")  # the app renders it as "| <id> |"


class OrderConfirmationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Thankyou for the order.")
        self.order_id_label = page.locator("label").filter(has_text=ORDER_ID)
        self.product_name = page.locator("tr.line-item .product-info-column .title").first

    @allure.step("Capture order ID and product name from confirmation page")
    def capture_order(self) -> dict:
        expect(self.heading).to_be_visible()
        expect(self.order_id_label).to_have_count(1)
        return {"order_id": ORDER_ID.search(self.order_id_label.inner_text()).group(0),
                "product_name": self.product_name.inner_text().strip()}
