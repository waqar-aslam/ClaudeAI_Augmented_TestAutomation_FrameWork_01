from datetime import date

import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Payment form"), allure.story("Expiry date")]


@allure.title("PAY-031 Expiry month list offers months 01 to 12")
def test_expiry_month_options_are_01_to_12(checkout_page):
    assert checkout_page.month_options() == [f"{m:02d}" for m in range(1, 13)]


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="KNOWN DEFECT D-09: expiry year list offers past years")
@allure.title("PAY-031 Expiry year list should not offer past years")
def test_expiry_year_options_are_not_in_the_past(checkout_page):
    this_year = date.today().year % 100
    past = [y for y in checkout_page.year_options() if int(y) < this_year]
    assert past == [], f"past expiry years offered: {past}"


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="KNOWN DEFECT D-08: app submits the order with an expired card (default 01/16)")
@allure.title("PAY-030 Checkout should not submit the order for an expired card")
def test_checkout_rejects_expired_card(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.select_expiry("01", "16")
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    submitted = checkout_page.place_order_and_detect_submission()

    assert not submitted, "order was submitted with an expired card (01/16)"


@allure.title("PAY-032 A card expiring in the current month and year is accepted")
def test_checkout_accepts_card_expiring_this_month(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    today = date.today()
    checkout_page.select_expiry(f"{today.month:02d}", f"{today.year % 100:02d}")
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    submitted = checkout_page.place_order_and_detect_submission()

    assert submitted, "a card valid through the current month must not be rejected"
