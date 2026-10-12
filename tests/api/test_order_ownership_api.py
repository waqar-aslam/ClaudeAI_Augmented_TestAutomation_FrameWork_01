import allure
import pytest

from config.settings import settings

pytestmark = [pytest.mark.api, allure.feature("Orders"), allure.story("Data integrity")]


@pytest.fixture
def order_details(api) -> list[dict]:
    """Details of every order the test user has. Read-only: this suite never creates orders itself.

    Checking all orders avoids assuming which one is "latest" (the list order is not guaranteed).
    """
    orders = api.get_orders()
    if not orders:
        pytest.skip("PRECONDITION: test user has no orders yet; run `pytest -m e2e` once to create one")
    return [api.get_order_details(o["_id"]) for o in orders]


@allure.title("PAY-071 Every order belongs to the authenticated test user")
def test_orders_belong_to_authenticated_user(api, order_details):
    foreign = [d["_id"] for d in order_details
               if d["orderById"] != api.user_id or d["orderBy"] != settings.user_email]
    assert foreign == [], f"orders not owned by the test user: {foreign}"


@allure.title("PAY-072 Order details match the catalogue product that was ordered")
def test_order_details_match_ordered_product(api, order_details):
    catalogue = {p["_id"]: p for p in api.get_products()}
    comparable = [d for d in order_details if d["productOrderedId"] in catalogue]
    if not comparable:
        pytest.skip("PRECONDITION: no order references a product that is still in the catalogue")

    mismatches = []
    for d in comparable:
        product = catalogue[d["productOrderedId"]]
        if (d["productName"], str(d["orderPrice"])) != (product["productName"], str(product["productPrice"])):
            mismatches.append(d["_id"])
        assert d["country"], f"order {d['_id']} has no country"
    assert mismatches == [], f"orders whose name/price differ from the catalogue: {mismatches}"
