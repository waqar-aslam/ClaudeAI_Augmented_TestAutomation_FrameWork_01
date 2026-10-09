import allure
import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

pytestmark = [pytest.mark.ui, allure.feature("Checkout validation")]


@pytest.fixture
def checkout(auth_page, clean_cart) -> CheckoutPage:
    """A checkout page for a cart holding one product (set up through the API)."""
    clean_cart.add_to_cart(clean_cart.get_products()[0])
    CartPage(auth_page).open_page().checkout()
    page = CheckoutPage(auth_page)
    page.payment_title.wait_for()
    return page


@allure.title("Checkout is blocked and no order is created when the country is missing")
def test_checkout_is_blocked_when_country_is_missing(checkout, api):
    orders_before = {o["_id"] for o in api.get_orders()}
    requests = checkout.capture_order_requests()
    checkout.cvv.fill("123")
    checkout.name_on_card.fill("QA Tester")

    checkout.place_order()

    checkout.expect_blocked_for_missing_shipping_info()
    assert requests == [], "create-order must not be sent without a country"
    assert {o["_id"] for o in api.get_orders()} <= orders_before


@allure.title("Checkout is blocked when the whole form is empty")
def test_checkout_is_blocked_when_form_is_empty(checkout):
    requests = checkout.capture_order_requests()

    checkout.place_order()

    checkout.expect_blocked_for_missing_shipping_info()
    assert requests == []


@pytest.mark.xfail(strict=True, reason="KNOWN DEFECT: app submits the order with an empty CVV (no validation)")
@allure.title("Checkout should not submit the order when CVV is empty")
def test_checkout_rejects_empty_cvv(checkout, checkout_data):
    requests = checkout.capture_order_requests()
    checkout.fill_details("", checkout_data["name_on_card"], checkout_data["country"])

    checkout.place_order()

    checkout.page.wait_for_load_state("networkidle")
    assert requests == [], "order was submitted with an empty CVV"


@pytest.mark.xfail(strict=True, reason="KNOWN DEFECT: app submits the order with an empty name on card (no validation)")
@allure.title("Checkout should not submit the order when name on card is empty")
def test_checkout_rejects_empty_name_on_card(checkout, checkout_data):
    requests = checkout.capture_order_requests()
    checkout.fill_details(checkout_data["cvv"], "", checkout_data["country"])

    checkout.place_order()

    checkout.page.wait_for_load_state("networkidle")
    assert requests == [], "order was submitted with an empty name on card"
