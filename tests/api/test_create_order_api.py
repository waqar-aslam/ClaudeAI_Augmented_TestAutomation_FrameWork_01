import allure
import pytest

pytestmark = [pytest.mark.api, allure.feature("API - Create order validation")]


@allure.title("Create-order rejects an unknown product id and creates no order")
def test_create_order_rejects_unknown_product_id(api):
    orders_before = {o["_id"] for o in api.get_orders()}

    response = api.create_order_raw({"orders": [{"country": "India", "productOrderedId": "000000000000000000000000"}]})

    assert response.status == 400
    assert response.json()["message"] == "Wrong Product ID"
    assert {o["_id"] for o in api.get_orders()} <= orders_before


@allure.title("Create-order requires an auth token")
def test_create_order_requires_token(anonymous_api):
    response = anonymous_api.create_order_raw({"orders": []}, authenticated=False)
    assert response.status == 401


@pytest.mark.xfail(strict=True, reason="KNOWN DEFECT: create-order returns 201 'Order Placed Successfully' for an empty orders list")
@allure.title("Create-order should reject an empty orders list")
def test_create_order_rejects_empty_orders_list(api):
    response = api.create_order_raw({"orders": []})
    assert response.status >= 400, f"got {response.status}: {response.text()[:100]}"


@pytest.mark.xfail(strict=True, reason="KNOWN DEFECT: create-order returns 500 (unhandled) when the body has no 'orders'")
@allure.title("Create-order should answer a missing orders field with a 4xx, not 500")
def test_create_order_rejects_missing_orders_field(api):
    response = api.create_order_raw({})
    assert 400 <= response.status < 500, f"got {response.status}"
