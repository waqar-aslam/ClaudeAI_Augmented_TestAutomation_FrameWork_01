import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Payment form"), allure.story("Required fields")]


@pytest.mark.xfail(strict=True, reason="KNOWN DEFECT D-03: app submits the order with an empty card number (no validation)")
@allure.title("PAY-013 Checkout should not submit the order when the card number is empty")
def test_checkout_rejects_empty_card_number(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.card_number.fill("")
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    checkout_page.place_order()

    checkout_page.page.wait_for_load_state("networkidle")
    assert order_requests == [], "order was submitted with an empty card number"
