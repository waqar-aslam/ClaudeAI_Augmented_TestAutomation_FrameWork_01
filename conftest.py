import allure
import pytest

from config.settings import settings


@pytest.fixture(scope="session")
def base_url() -> str:
    return settings.base_url


@pytest.fixture(scope="session")
def credentials() -> dict:
    if not (settings.user_email and settings.user_password):
        pytest.skip("USER_EMAIL / USER_PASSWORD not set (see .env.example)")
    return {"email": settings.user_email, "password": settings.user_password}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    # Runs while fixtures are still alive, so the browser page can still be captured.
    page = next((v for k, v in item.funcargs.items() if k in ("page", "auth_page")), None)
    if page is not None and not page.is_closed():
        # Payment fields are masked so card data never lands in the report.
        sensitive = [page.locator(".payment__info input"), page.locator("input[type=password]")]
        allure.attach(page.screenshot(mask=sensitive), name="failure-screenshot",
                      attachment_type=allure.attachment_type.PNG)
        allure.attach(page.url, name="url", attachment_type=allure.attachment_type.TEXT)


# --- API fixtures -------------------------------------------------------------
from api.client import ApiClient  # noqa: E402


@pytest.fixture(scope="session")
def api_context(playwright):
    context = playwright.request.new_context(base_url=settings.api_url + "/")
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def anonymous_api(api_context) -> ApiClient:
    return ApiClient(api_context)


@pytest.fixture(scope="session")
def api(api_context, credentials) -> ApiClient:
    """API client authenticated as the practice user."""
    return ApiClient(api_context).authenticate(credentials["email"], credentials["password"])


@pytest.fixture
def clean_cart(api):
    """Start and finish with an empty cart so tests stay independent."""
    api.clear_cart()
    yield api
    api.clear_cart()


# --- UI fixtures --------------------------------------------------------------
import json  # noqa: E402
from pathlib import Path  # noqa: E402


@pytest.fixture
def auth_page(context, api):
    """A page that is already logged in: the token is in localStorage before the app boots."""
    context.add_init_script(f"window.localStorage.setItem('token', {json.dumps(api.token)})")
    return context.new_page()


@pytest.fixture(scope="session")
def checkout_data() -> dict:
    return json.loads((Path(__file__).parent / "test_data" / "checkout.json").read_text())


@pytest.fixture(scope="session")
def payment_data() -> dict:
    return json.loads((Path(__file__).parent / "test_data" / "payment.json").read_text())


@pytest.fixture
def checkout_page(auth_page, clean_cart):
    """Checkout page for a cart holding one product (seeded via the API); the product is on `.product`."""
    from pages.cart_page import CartPage
    from pages.checkout_page import CheckoutPage

    product = clean_cart.get_products()[0]
    clean_cart.add_to_cart(product)
    CartPage(auth_page).open_page().checkout()
    page = CheckoutPage(auth_page)
    page.payment_title.wait_for()
    page.product = product
    return page


@pytest.fixture
def order_requests(checkout_page) -> list:
    """create-order bodies sent by the page; each request is aborted so no real order is created."""
    return checkout_page.capture_order_requests()
