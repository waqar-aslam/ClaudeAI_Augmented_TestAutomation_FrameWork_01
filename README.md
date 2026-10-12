# QA Automation Framework - Let's Shop (practice app)

Python + Pytest + Playwright (UI and API) + Page Object Model + Allure, with a Claude Code `qa-test-agent` subagent.

Target: https://rahulshettyacademy.com/client (a public practice app; the shared backend is not under our control).

## Setup (Windows / PyCharm)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env      # then fill in USER_EMAIL and USER_PASSWORD
```

`.env` is git-ignored. Never put credentials in source files, logs or reports.

| Variable | Purpose |
|---|---|
| `BASE_URL` | UI root, default `https://rahulshettyacademy.com/client` |
| `API_URL` | API root, default `https://rahulshettyacademy.com/api/ecom` |
| `USER_EMAIL` / `USER_PASSWORD` | Practice account. Tests needing them are skipped if unset. |

## Running tests

```powershell
pytest                      # everything except e2e (results go to allure-results/ and accumulate)
pytest -m api               # API only (fast, no browser)
pytest -m ui                # UI only
pytest -m e2e               # end-to-end flow; opt-in because it places a REAL order
pytest -m creates_data      # opt-in: tests that may create records (e.g. create-order with an empty list)
pytest tests/ui --headed    # watch the browser
```

## Allure report

The Allure CLI is a separate install (it is not a pip package), e.g. `scoop install allure` or `npm i -g allure-commandline`.

```powershell
allure serve allure-results
```

`allure-results/` is no longer wiped automatically; delete it before a run you want to report on (`Remove-Item -Recurse allure-results`).
Each run also writes `environment.properties` (URLs only) and `categories.json` (known defects are grouped separately from skips and failures).

Failed UI tests (including setup errors) attach a screenshot with **every input masked** and the page URL. Login payloads and tokens are never attached, and credentials/card data are never recorded as step parameters. After a run, verify with:

```powershell
python -m utils.scan_allure_results      # exits 1 if the password, e-mail or a card number is found
```

## Layout

```
config/settings.py     env-based settings
utils/                 report-safety helpers (scan_allure_results, payment_data)
api/client.py          ApiClient over Playwright APIRequestContext
pages/                 Page Objects (locators + interactions + page checks); BasePage is the parent
tests/ui|api|e2e/      tests describe business behaviour only
test_data/             dummy checkout data
conftest.py            fixtures: api, clean_cart, auth_page, checkout_page, order_requests, wrong_password; failure screenshots; Allure metadata
.claude/agents/        qa-test-agent subagent
```

Key fixtures: `api` (authenticated API client, session-scoped), `clean_cart` (empties the cart before and after a test), `auth_page` (a browser page already logged in, with the token injected before the app starts).

## What the app actually does (verified against live responses)

- Auth: `POST /api/ecom/auth/login` returns `{token, userId, message}`. The token is sent as a raw `Authorization` header with no `Bearer` prefix. Wrong credentials return 400 `Incorrect email or password.`; requests without a token return 401.
- Products: `POST product/get-all-products`. Cart: `POST user/add-to-cart` with `{_id: userId, product: {...}}`, `GET user/get-cart-products/{userId}` (items under `products`), `GET user/get-cart-count/{userId}`, `DELETE user/remove-from-cart/{userId}/{productId}`.
- Orders: `POST order/create-order`, `GET order/get-orders-for-customer/{userId}`, `GET order/get-orders-details?id={orderId}`.
- UI routes: `#/auth/login`, `#/dashboard/dash`, `#/dashboard/cart`, `#/dashboard/order` (checkout), `#/dashboard/thanks`, `#/dashboard/myorders`, `#/dashboard/order-details/{id}`.

## Known limitations and notes

- **The end-to-end test places a real demo order each run it is selected** (`pytest -m e2e`; excluded from the default run via `-m "not e2e"` in `pytest.ini`). Orders cannot be removed without the destructive `delete-order` endpoint, which this framework never calls. The backend seems to keep only the 7 newest orders per user, so tests match orders by ID and never assert on counts.
- **Shared account and backend:** other users or runs can change the data. Tests pick products at runtime instead of hard-coding names.
- **Possible application defect:** `GET order/get-orders-details?id=<malformed id>` returns HTTP 500 with Mongoose/MongoDB error details. Not asserted as expected behaviour.
- **Data oddity:** in older orders `productOrderedId` contains a date string and `orderDate` is null; use `_id` as the order ID.
- The UI only authenticates when the token is in `localStorage` before the app boots, hence `add_init_script` in `auth_page`.
- The checkout card number is pre-filled by the app and left untouched; CVV and name use dummy values from `test_data/checkout.json`.

## Claude Code QA agent

`.claude/agents/qa-test-agent.md` defines the `qa-test-agent` subagent. Ask Claude Code, for example: "Use qa-test-agent to cover removing an item from the cart", and it will analyse scenarios, implement tests following the POM conventions, run them, classify failures (application / automation / environment / test-data) and report truthfully.
