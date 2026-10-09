import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Payment form"), allure.story("Input validation")]


def _defect(defect_id: str, text: str):
    return pytest.mark.xfail(strict=True, reason=f"KNOWN DEFECT {defect_id}: {text}")


def _case(case_id, defect_id, text, **overrides):
    return pytest.param(overrides, id=case_id, marks=_defect(defect_id, text))


CASES = [
    _case("PAY-020-cvv-non-numeric", "D-04", "non-numeric CVV is accepted", cvv="non_numeric_cvv"),
    _case("PAY-021-card-number-too-long", "D-05", "no length limit on card number", card_number="too_long"),
    _case("PAY-021-cvv-too-long", "D-05", "no length limit on CVV", cvv="too_long"),
    _case("PAY-021-name-too-long", "D-05", "no length limit on name on card", name_on_card="too_long"),
    _case("PAY-022-card-number-malformed", "D-06", "malformed card number is accepted", card_number="malformed"),
    _case("PAY-023-name-with-symbols", "D-07", "digits/symbols accepted in name on card", name_on_card="symbols"),
]


def _value(field: str, key: str, payment_data: dict) -> str:
    if key == "too_long":
        too_long = payment_data["too_long"]
        return "A" * too_long["name_on_card_length"] if field == "name_on_card" else too_long[field]
    return {"non_numeric_cvv": payment_data["non_numeric_cvv"],
            "malformed": payment_data["malformed_card_number"],
            "symbols": payment_data["name_with_symbols"]}[key]


@allure.title("Checkout should not submit the order when a payment field holds an invalid value")
@pytest.mark.parametrize("overrides", CASES)
def test_checkout_rejects_invalid_payment_value(checkout_page, order_requests, payment_data, overrides):
    valid = dict(payment_data["valid"])
    for field, key in overrides.items():
        valid[field] = _value(field, key, payment_data)
    allure.dynamic.description(f"Invalid field(s): {', '.join(overrides)} (values not attached to protect card data)")

    checkout_page.card_number.fill(valid["card_number"])
    checkout_page.fill_details(valid["cvv"], valid["name_on_card"], valid["country"])
    checkout_page.place_order()

    checkout_page.page.wait_for_load_state("networkidle")
    assert order_requests == [], f"order was submitted with invalid {', '.join(overrides)}"
