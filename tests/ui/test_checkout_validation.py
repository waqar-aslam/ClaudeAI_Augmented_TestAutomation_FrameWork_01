import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Checkout validation")]


@allure.title("Checkout is blocked and no order is created when the country is missing")
def test_checkout_is_blocked_when_country_is_missing(checkout_page, api):
    orders_before = {o["_id"] for o in api.get_orders()}
    requests = checkout_page.capture_order_requests()
    checkout_page.cvv.fill("123")
    checkout_page.name_on_card.fill("QA Tester")

    checkout_page.place_order()

    checkout_page.expect_blocked_for_missing_shipping_info()
    assert requests == [], "create-order must not be sent without a country"
    assert {o["_id"] for o in api.get_orders()} <= orders_before


@allure.title("Checkout is blocked when the whole form is empty")
def test_checkout_is_blocked_when_form_is_empty(checkout_page):
    requests = checkout_page.capture_order_requests()

    checkout_page.place_order()

    checkout_page.expect_blocked_for_missing_shipping_info()
    assert requests == []


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="KNOWN DEFECT: app submits the order with an empty CVV (no validation)")
@allure.title("Checkout should not submit the order when CVV is empty")
def test_checkout_rejects_empty_cvv(checkout_page, checkout_data):
    requests = checkout_page.capture_order_requests()
    checkout_page.fill_details("", checkout_data["name_on_card"], checkout_data["country"])

    submitted = checkout_page.place_order_and_detect_submission()

    assert not submitted, "order was submitted with an empty CVV"


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="KNOWN DEFECT: app submits the order with an empty name on card (no validation)")
@allure.title("Checkout should not submit the order when name on card is empty")
def test_checkout_rejects_empty_name_on_card(checkout_page, checkout_data):
    requests = checkout_page.capture_order_requests()
    checkout_page.fill_details(checkout_data["cvv"], "", checkout_data["country"])

    submitted = checkout_page.place_order_and_detect_submission()

    assert not submitted, "order was submitted with an empty name on card"
