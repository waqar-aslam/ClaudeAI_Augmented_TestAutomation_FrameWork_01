import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_title = page.get_by_text("Payment Method")
        self.card_number = self._field("Credit Card Number")
        self.expiry_month = page.locator("select.ddl").nth(0)
        self.expiry_year = page.locator("select.ddl").nth(1)
        self.cvv = self._field("CVV Code")
        self.name_on_card = self._field("Name on Card")
        self.coupon = page.locator("input[name=coupon]")
        self.apply_coupon_button = page.get_by_role("button", name="Apply Coupon")
        self.invalid_coupon_message = page.get_by_text("* Invalid Coupon")
        self.country = page.get_by_placeholder("Select Country")
        self.country_options = page.locator(".ta-results button")
        self.place_order_button = page.get_by_text("Place Order")
        self.payment_tabs = page.locator(".payment__type")

    def _field(self, title: str):
        return self.page.locator(".field").filter(has_text=title).locator("input")

    @allure.step("Fill checkout details")
    def fill_details(self, cvv: str, name_on_card: str, country: str) -> None:
        expect(self.payment_title).to_be_visible()
        self.cvv.fill(cvv)
        self.name_on_card.fill(name_on_card)
        self.choose_country(country)

    @allure.step("Choose country '{country}' from the suggestions")
    def choose_country(self, country: str) -> None:
        self.country.press_sequentially(country[:3], delay=50)
        option = self.country_options.filter(has_text=re.compile(rf"^\s*{re.escape(country)}\s*$"))
        option.click()

    @allure.step("Type country '{text}' without choosing a suggestion")
    def type_country_without_selecting(self, text: str) -> None:
        self.country.fill(text)

    @allure.step("Select expiry {month}/{year}")
    def select_expiry(self, month: str, year: str) -> None:
        self.expiry_month.select_option(month)
        self.expiry_year.select_option(year)

    def year_options(self) -> list[str]:
        return self.expiry_year.locator("option").all_inner_texts()

    def month_options(self) -> list[str]:
        return self.expiry_month.locator("option").all_inner_texts()

    @allure.step("Apply coupon")
    def apply_coupon(self, code: str) -> None:
        self.coupon.fill(code)
        self.apply_coupon_button.click()

    @allure.step("Place order")
    def place_order(self) -> None:
        self.place_order_button.click()

    @allure.step("Place order while the country suggestion list is still open")
    def place_order_with_suggestions_open(self) -> None:
        # The suggestion list's backdrop covers the button, so a real click would be intercepted.
        self.place_order_button.dispatch_event("click")

    @allure.step("Verify checkout summary shows {name}, ${price}, quantity {quantity}")
    def expect_summary(self, name: str, price: int | str, quantity: int = 1) -> None:
        expect(self.page.get_by_text(name, exact=True)).to_be_visible()
        expect(self.page.get_by_text(f"$ {price}", exact=True).first).to_be_visible()
        expect(self.page.get_by_text(f"Quantity: {quantity}")).to_be_visible()

    @allure.step("Verify checkout is blocked with the shipping-information message")
    def expect_blocked_for_missing_shipping_info(self) -> None:
        self.expect_toast("Please Enter Full Shipping Information")
        expect(self.page).to_have_url(re.compile(r"#/dashboard/order\?"))

    @allure.step("Verify the order failed with an error message and the user stays on checkout")
    def expect_order_error(self) -> None:
        self.expect_toast("Unknown error occured")
        expect(self.page).to_have_url(re.compile(r"#/dashboard/order\?"))

    def capture_order_requests(self) -> list:
        """Intercept create-order: record the request body and abort it so no real order is placed."""
        captured: list = []

        def handler(route):
            captured.append(route.request.post_data)
            route.abort()

        self.page.route("**/order/create-order", handler)
        return captured
