"""Thin wrapper over Playwright's APIRequestContext for the /api/ecom endpoints.

Endpoint paths, methods and payloads were taken from the app's own client code and
confirmed against live responses. Credentials and tokens are never logged or attached.
"""
import allure
from playwright.sync_api import APIRequestContext, APIResponse


class ApiClient:
    def __init__(self, context: APIRequestContext, token: str | None = None, user_id: str | None = None):
        self.context = context
        self.token = token
        self.user_id = user_id

    @property
    def _headers(self) -> dict:
        # The app sends the raw JWT, with no "Bearer " prefix.
        return {"Authorization": self.token} if self.token else {}

    # --- auth -------------------------------------------------------------
    def login_raw(self, email: str, password: str) -> APIResponse:
        return self.context.post("auth/login", data={"userEmail": email, "userPassword": password})

    def authenticate(self, email: str, password: str) -> "ApiClient":
        body = self.login_raw(email, password).json()
        self.token, self.user_id = body["token"], body["userId"]
        return self

    # --- products ---------------------------------------------------------
    def get_products_raw(self, authenticated: bool = True) -> APIResponse:
        return self.context.post("product/get-all-products", data={},
                                 headers=self._headers if authenticated else {})

    def get_products(self) -> list[dict]:
        return self.get_products_raw().json()["data"]

    # --- cart -------------------------------------------------------------
    @allure.step("API: add product to cart")
    def add_to_cart(self, product: dict) -> APIResponse:
        return self.context.post("user/add-to-cart", headers=self._headers,
                                 data={"_id": self.user_id, "product": product})

    def get_cart_products(self) -> list[dict]:
        body = self.context.get(f"user/get-cart-products/{self.user_id}", headers=self._headers).json()
        return body.get("products", [])  # key is absent when the cart is empty

    def get_cart_count(self) -> int:
        body = self.context.get(f"user/get-cart-count/{self.user_id}", headers=self._headers).json()
        return body.get("count", 0)

    def remove_from_cart(self, product_id: str) -> APIResponse:
        return self.context.delete(f"user/remove-from-cart/{self.user_id}/{product_id}", headers=self._headers)

    @allure.step("API: empty the test user's cart")
    def clear_cart(self) -> None:
        for item in self.get_cart_products():
            self.remove_from_cart(item["_id"])

    # --- orders -----------------------------------------------------------
    def create_order_raw(self, body: dict, authenticated: bool = True) -> APIResponse:
        return self.context.post("order/create-order", data=body,
                                 headers=self._headers if authenticated else {})

    def get_orders(self) -> list[dict]:
        return self.context.get(f"order/get-orders-for-customer/{self.user_id}",
                                headers=self._headers).json().get("data") or []

    def get_order_details_raw(self, order_id: str) -> APIResponse:
        return self.context.get(f"order/get-orders-details?id={order_id}", headers=self._headers)

    def get_order_details(self, order_id: str) -> dict:
        return self.get_order_details_raw(order_id).json()["data"]
