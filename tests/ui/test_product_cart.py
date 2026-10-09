import allure
import pytest

from pages.cart_page import CartPage
from pages.dashboard_page import DashboardPage

pytestmark = [pytest.mark.ui, allure.feature("Product & Cart")]


@allure.title("User can add a product to the cart and see it in the cart")
def test_user_can_add_product_to_cart(auth_page, clean_cart):
    dashboard = DashboardPage(auth_page).open_page()
    product = dashboard.product_names()[0]

    dashboard.add_to_cart(product)
    dashboard.open_cart()

    CartPage(auth_page).expect_product(product)
    assert clean_cart.get_cart_count() == 1  # UI action is reflected in the backend
