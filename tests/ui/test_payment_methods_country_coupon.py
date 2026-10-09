import allure
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.ui, allure.feature("Payment form")]


@allure.story("Checkout summary")
@allure.title("PAY-003 Checkout summary matches the product in the cart")
def test_checkout_summary_matches_cart_product(checkout_page):
    product = checkout_page.product

    checkout_page.expect_summary(product["productName"], product["productPrice"], quantity=1)


@allure.story("Defaults")
@allure.title("PAY-040 Checkout opens on Credit Card with the documented default card and expiry")
def test_checkout_defaults(checkout_page, payment_data):
    expect(checkout_page.payment_tabs.filter(has_text="Credit Card")).to_have_class("payment__type payment__type--cc active")
    expect(checkout_page.card_number).to_have_value(payment_data["valid"]["card_number"])
    expect(checkout_page.expiry_month).to_have_value("01")
    expect(checkout_page.expiry_year).to_have_value("16")


@allure.story("Country")
@allure.title("PAY-002 Country suggestions match the typed text and selection fills the field")
def test_country_suggestions_and_selection(checkout_page):
    checkout_page.country.press_sequentially("ind", delay=50)
    expect(checkout_page.country_options).to_have_text(["British Indian Ocean Territory", "India", "Indonesia"])

    checkout_page.country_options.filter(has_text="Indonesia").click()

    expect(checkout_page.country).to_have_value("Indonesia")


@allure.story("Country")
@allure.title("PAY-043 Typing a country name without choosing a suggestion does not count as a selected country")
def test_country_typed_without_selection_is_blocked(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.cvv.fill(valid["cvv"])
    checkout_page.name_on_card.fill(valid["name_on_card"])
    checkout_page.type_country_without_selecting(valid["country"])

    checkout_page.place_order_with_suggestions_open()

    checkout_page.expect_blocked_for_missing_shipping_info()
    assert order_requests == []


@allure.story("Coupon")
@allure.title("PAY-050 An invalid coupon shows an inline error")
def test_invalid_coupon_shows_error(checkout_page):
    checkout_page.apply_coupon("INVALID-QA")

    expect(checkout_page.invalid_coupon_message).to_be_visible()
