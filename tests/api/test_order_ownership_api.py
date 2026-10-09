import allure
import pytest

from config.settings import settings

pytestmark = [pytest.mark.api, allure.feature("Orders"), allure.story("Data integrity")]


@pytest.fixture
def latest_order(api) -> dict:
    orders = api.get_orders()
    if not orders:
        pytest.skip("test user has no orders yet; run the e2e order test first")
    return api.get_order_details(orders[-1]["_id"])


@allure.title("PAY-071 An order belongs to the authenticated test user")
def test_order_belongs_to_authenticated_user(api, latest_order):
    assert latest_order["orderById"] == api.user_id
    assert latest_order["orderBy"] == settings.user_email


@allure.title("PAY-072 Order details match the product that was ordered")
def test_order_details_match_ordered_product(api, latest_order):
    product = next((p for p in api.get_products() if p["_id"] == latest_order["productOrderedId"]), None)
    if product is None:
        pytest.skip("ordered product is no longer in the catalogue")

    assert latest_order["productName"] == product["productName"]
    assert str(latest_order["orderPrice"]) == str(product["productPrice"])
    assert latest_order["country"]
