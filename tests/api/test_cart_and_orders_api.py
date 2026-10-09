import allure
import pytest

pytestmark = [pytest.mark.api, allure.feature("API - Cart & Orders")]


@allure.title("Added product appears in the cart and the cart count increases")
def test_added_product_appears_in_cart_and_count(clean_cart):
    product = clean_cart.get_products()[0]
    assert clean_cart.get_cart_count() == 0

    response = clean_cart.add_to_cart(product)

    assert response.status == 200
    assert clean_cart.get_cart_count() == 1
    assert [p["_id"] for p in clean_cart.get_cart_products()] == [product["_id"]]


@allure.title("Removing a product empties the cart")
def test_removed_product_disappears_from_cart(clean_cart):
    product = clean_cart.get_products()[0]
    clean_cart.add_to_cart(product)

    response = clean_cart.remove_from_cart(product["_id"])

    assert response.status == 200
    assert clean_cart.get_cart_count() == 0


@allure.title("Order details API matches the order returned in the order list")
def test_order_details_match_order_list_entry(api):
    orders = api.get_orders()
    if not orders:
        pytest.skip("test user has no orders yet (data precondition)")
    listed = orders[0]

    details = api.get_order_details(listed["_id"])

    for field in ("_id", "productName", "orderPrice", "country", "orderBy"):
        assert details[field] == listed[field], field


@allure.title("Order details API returns an error for an unknown order id")
def test_order_details_rejects_unknown_order_id(api):
    response = api.get_order_details_raw("000000000000000000000000")
    assert response.status == 400
    assert response.json()["message"] == "Order not found"
