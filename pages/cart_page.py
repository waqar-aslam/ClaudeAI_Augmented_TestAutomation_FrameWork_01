import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="My Cart")
        self.items = page.locator("ul.cartWrap li.items")
        self.checkout_button = page.get_by_role("button", name="Checkout")

    @allure.step("Open cart page")
    def open_page(self) -> "CartPage":
        self.open("dashboard/cart")
        expect(self.heading).to_be_visible()
        return self

    @allure.step("Verify cart contains product: {product_name}")
    def expect_product(self, product_name: str) -> None:
        expect(self.heading).to_be_visible()
        expect(self.items).to_have_count(1)
        expect(self.items.first.get_by_role("heading", name=product_name, exact=True)).to_be_visible()

    @allure.step("Proceed to checkout")
    def checkout(self) -> None:
        self.checkout_button.click()
