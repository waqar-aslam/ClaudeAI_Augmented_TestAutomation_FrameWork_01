import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class DashboardPage(BasePage):
    ROUTE = "dashboard/dash"

    def __init__(self, page: Page):
        super().__init__(page)
        self.cards = page.locator(".card-body")
        self.cart_button = page.locator("button[routerlink='/dashboard/cart']")  # nav button; role+name also matches 'Add To Cart'

    def _card(self, product_name: str):
        return self.cards.filter(has=self.page.get_by_role("heading", name=product_name, exact=True))

    @allure.step("Open dashboard")
    def open_page(self) -> "DashboardPage":
        self.open(self.ROUTE)
        expect(self.cards.first).to_be_visible()
        return self

    @allure.step("Verify authenticated dashboard is shown")
    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.url(self.ROUTE))
        expect(self.cards.first).to_be_visible()

    def product_names(self) -> list[str]:
        expect(self.cards.first).to_be_visible()
        return [t.strip() for t in self.cards.locator("h5").all_inner_texts()]

    @allure.step("Add product to cart: {product_name}")
    def add_to_cart(self, product_name: str) -> None:
        self._card(product_name).get_by_role("button", name="Add To Cart").click()
        self.expect_toast("Product Added To Cart")

    @allure.step("Open cart")
    def open_cart(self) -> None:
        self.cart_button.click()
