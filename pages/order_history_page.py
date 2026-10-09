import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class OrderHistoryPage(BasePage):
    ROUTE = "dashboard/myorders"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Your Orders")
        self.rows = page.locator("tbody tr")

    def _row(self, order_id: str):
        return self.rows.filter(has=self.page.locator("th", has_text=order_id))

    @allure.step("Open order history")
    def open_page(self) -> "OrderHistoryPage":
        self.open(self.ROUTE)
        expect(self.heading).to_be_visible()
        return self

    @allure.step("Read order {order_id} from order history")
    def read_order(self, order_id: str) -> dict:
        row = self._row(order_id)
        expect(row).to_have_count(1)
        return {"order_id": row.locator("th").inner_text().strip(),
                "product_name": row.locator("td").nth(1).inner_text().strip(),
                "price": row.locator("td").nth(2).inner_text().strip()}

    @allure.step("Open order details for {order_id}")
    def open_details(self, order_id: str) -> None:
        self._row(order_id).get_by_role("button", name="View").click()
        expect(self.page).to_have_url(self.url(f"dashboard/order-details/{order_id}"))
