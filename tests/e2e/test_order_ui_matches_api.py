import allure
import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.dashboard_page import DashboardPage
from pages.order_confirmation_page import OrderConfirmationPage
from pages.order_history_page import OrderHistoryPage

pytestmark = [pytest.mark.e2e, allure.feature("Checkout")]


@allure.title("Placed order ID and product name match the order API response")
@allure.description(
    "Add a product, check out, capture the order from the confirmation page, then verify it in "
    "Order History and against GET order/get-orders-details. This places a real demo order.")
def test_placed_order_matches_api_response(auth_page, clean_cart, checkout_data):
    dashboard = DashboardPage(auth_page).open_page()
    product = dashboard.product_names()[0]
    price = next(p["productPrice"] for p in clean_cart.get_products() if p["productName"] == product)

    dashboard.add_to_cart(product)
    dashboard.open_cart()
    cart = CartPage(auth_page)
    cart.expect_product(product)
    cart.checkout()

    checkout = CheckoutPage(auth_page)
    checkout.fill_details(checkout_data["cvv"], checkout_data["name_on_card"], checkout_data["country"])
    checkout.place_order()

    placed = OrderConfirmationPage(auth_page).capture_order()
    allure.attach(str(placed), name="captured order (UI)", attachment_type=allure.attachment_type.TEXT)
    assert placed["product_name"] == product

    history = OrderHistoryPage(auth_page)
    history.open_page()
    listed = history.read_order(placed["order_id"])
    assert listed["product_name"] == product

    with allure.step("Compare UI values with order API response"):
        api_order = clean_cart.get_order_details(placed["order_id"])
        assert api_order["_id"] == placed["order_id"] == listed["order_id"]
        assert api_order["productName"] == placed["product_name"] == listed["product_name"]
        assert api_order["country"] == checkout_data["country"]
        assert listed["price"] == f"$ {price}" and api_order["orderPrice"] == str(price)

    history.open_details(placed["order_id"])
