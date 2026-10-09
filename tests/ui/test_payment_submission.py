import json

import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Payment form"), allure.story("Submission")]


@allure.title("PAY-061 A failed create-order call shows an error and keeps the user on checkout")
def test_order_failure_shows_error_and_keeps_user_on_checkout(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])

    checkout_page.place_order()

    checkout_page.expect_order_error()
    assert len(order_requests) == 1


@allure.title("PAY-062 After a blocked submit the user can fix the country and resubmit")
def test_user_can_correct_missing_country_and_resubmit(checkout_page, order_requests, payment_data):
    valid = payment_data["valid"]
    checkout_page.cvv.fill(valid["cvv"])
    checkout_page.name_on_card.fill(valid["name_on_card"])
    checkout_page.place_order()
    checkout_page.expect_blocked_for_missing_shipping_info()
    assert order_requests == []

    checkout_page.choose_country(valid["country"])
    with checkout_page.page.expect_request("**/order/create-order"):
        checkout_page.place_order()

    assert json.loads(order_requests[0])["orders"][0]["country"] == valid["country"]


@allure.title("PAY-070 Card number, expiry, CVV and name are never sent to the server")
def test_payment_fields_are_not_sent_to_create_order(checkout_page, order_requests, payment_data):
    distinct = payment_data["distinct_card_values"]
    checkout_page.card_number.fill(distinct["card_number"])
    checkout_page.select_expiry("12", "31")
    checkout_page.fill_details(distinct["cvv"], distinct["name_on_card"], payment_data["valid"]["country"])

    with checkout_page.page.expect_request("**/order/create-order"):
        checkout_page.place_order()

    body = json.loads(order_requests[0])
    assert set(body) == {"orders"}
    assert set(body["orders"][0]) == {"country", "productOrderedId"}
    raw = order_requests[0]
    for secret in (distinct["card_number"], distinct["card_number"].replace(" ", ""), distinct["cvv"],
                   distinct["name_on_card"]):
        assert secret not in raw, "payment data leaked into the create-order request"
