import allure
import pytest

from api.client import ApiClient

pytestmark = [pytest.mark.api, allure.feature("API - Auth & Products")]


@allure.title("Login API returns a token and user id for valid credentials")
def test_login_returns_token_and_user_id(api_context, credentials):
    response = ApiClient(api_context).login_raw(credentials["email"], credentials["password"])
    body = response.json()
    assert response.status == 200
    assert body["message"] == "Login Successfully"
    assert body["token"] and body["userId"]


@allure.title("Login API rejects a wrong password with 400")
def test_login_is_rejected_for_wrong_password(anonymous_api, credentials):
    response = anonymous_api.login_raw(credentials["email"], "Wrong#Pass-1")
    assert response.status == 400
    assert response.json()["message"] == "Incorrect email or password."


@allure.title("Products API requires an auth token")
def test_products_are_not_available_without_token(anonymous_api):
    assert anonymous_api.get_products_raw(authenticated=False).status == 401


@allure.title("Products API returns products with the fields the UI relies on")
def test_products_list_has_expected_fields(api):
    products = api.get_products()
    assert products, "expected at least one product"
    for product in products:
        assert product["_id"] and product["productName"]
        assert isinstance(product["productPrice"], int) and product["productPrice"] > 0
