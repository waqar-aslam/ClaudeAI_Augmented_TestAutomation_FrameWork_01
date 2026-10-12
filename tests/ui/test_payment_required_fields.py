import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Payment form"), allure.story("Required fields")]


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="KNOWN DEFECT D-03: app submits the order with an empty card number (no validation)")
@allure.title("PAY-013 Checkout should not submit the order when the card number is empty")
def test_checkout_rejects_empty_card_number(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.card_number.fill("")
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    submitted = checkout_page.place_order_and_detect_submission()

    assert not submitted, "order was submitted with an empty card number"


@allure.title("PAY-015 Checkout is blocked when the shipping e-mail is empty")
def test_checkout_is_blocked_when_shipping_email_is_empty(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.shipping_email.fill("")
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    checkout_page.place_order()

    checkout_page.expect_blocked_for_missing_shipping_info()
    assert order_requests == []


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="KNOWN DEFECT D-10: app submits the order with a malformed shipping e-mail")
@allure.title("PAY-015 Checkout should not submit the order when the shipping e-mail is malformed")
def test_checkout_rejects_malformed_shipping_email(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.shipping_email.fill(payment_data["invalid_email"])
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    submitted = checkout_page.place_order_and_detect_submission()

    assert not submitted, "order was submitted with a malformed shipping e-mail"
