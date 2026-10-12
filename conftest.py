import json
from pathlib import Path

import allure
import pytest

from api.client import ApiClient
from config.settings import settings


@pytest.fixture(scope="session")
def base_url() -> str:
    return settings.base_url


@pytest.fixture(scope="session")
def credentials() -> dict:
    if not (settings.user_email and settings.user_password):
        pytest.skip("USER_EMAIL / USER_PASSWORD not set (see .env.example)")
    return {"email": settings.user_email, "password": settings.user_password}


@pytest.fixture(scope="session")
def wrong_password() -> str:
    """A password that is not the practice account's (used by login-rejection tests)."""
    return "Wrong#Pass-1"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return
    # Runs while fixtures are still alive, so the browser page can still be captured
    # (also for setup errors, e.g. a broken checkout fixture).
    page = next((v for k, v in item.funcargs.items() if k in ("page", "auth_page")), None)
    if page is not None and not page.is_closed():
        # Every input is masked (card data, CVV, name, coupon, e-mail, password) so none lands in the report.
        sensitive = [page.locator("input, textarea")]
        allure.attach(page.screenshot(mask=sensitive), name="failure-screenshot",
                      attachment_type=allure.attachment_type.PNG)
        allure.attach(page.url, name="url", attachment_type=allure.attachment_type.TEXT)


def pytest_collection_modifyitems(config, items):
    """Skip tests that may create backend data (orders cannot be deleted) unless explicitly selected."""
    if "creates_data" in (config.option.markexpr or ""):
        return
    skip = pytest.mark.skip(reason="may create data on the shared backend; opt in with: pytest -m creates_data")
    for item in items:
        if item.get_closest_marker("creates_data"):
            item.add_marker(skip)


# --- Allure run metadata ------------------------------------------------------
# Written at session end (not session start) so the files survive allure-pytest's own setup.
KNOWN_DEFECT_CATEGORIES = [
    {"name": "Known application defects (strict xfail)", "matchedStatuses": ["skipped"],
     "messageRegex": ".*KNOWN DEFECT.*"},
    {"name": "Skipped (data/environment precondition)", "matchedStatuses": ["skipped"]},
    {"name": "Assertion failures", "matchedStatuses": ["failed"], "messageRegex": ".*AssertionError.*"},
    {"name": "Automation/environment errors", "matchedStatuses": ["broken", "failed"]},
]


def pytest_sessionfinish(session, exitstatus):
    results_dir = getattr(session.config.option, "allure_report_dir", None)
    if not results_dir:
        return
    out = Path(results_dir)
    out.mkdir(parents=True, exist_ok=True)
    # No credentials: only non-sensitive endpoints and the run selection.
    environment = {"base_url": settings.base_url, "api_url": settings.api_url,
                   "markers": session.config.option.markexpr or "(none)"}
    lines = [f"{k}={v}" for k, v in environment.items()]
    (out / "environment.properties").write_text("\n".join(lines) + "\n")
    (out / "categories.json").write_text(json.dumps(KNOWN_DEFECT_CATEGORIES, indent=2))


# --- API fixtures -------------------------------------------------------------


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
def stubbed_order_requests(checkout_page) -> list:
    """create-order bodies sent by the page; each is answered with a fake 201, so no real order is created."""
    return checkout_page.stub_order_success()


@pytest.fixture
def order_requests(checkout_page) -> list:
    """create-order bodies sent by the page; each request is aborted so no real order is created."""
    return checkout_page.capture_order_requests()
