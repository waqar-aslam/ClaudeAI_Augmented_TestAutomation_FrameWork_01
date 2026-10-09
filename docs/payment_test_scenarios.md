# Checkout & Payment Form – Test Scenarios

Application: Let's Shop practice app – `https://rahulshettyacademy.com/client` (Angular SPA, API at `/api/ecom`).
Explored: 2026-10-09 with Playwright MCP (Chrome), user `aslamwaqar313@gmail.com`. Credentials are read from `.env` (`USER_EMAIL` / `USER_PASSWORD`); none are stored in this document.

Status legend: **Confirmed** = observed in the browser/network this session · **Requires Investigation** = not proven, needs a further probe · **Not Applicable** = control does not allow the condition.
Evidence legend: **[C]** confirmed by observation · **[I]** inferred · **[?]** unknown.

---

## 1. Observed behaviour (Checkpoint 1)

### User journey
| Step | Observed |
|---|---|
| Login `#/auth/login` | Email + password + Login button, Register and Forgot-password links. `POST /auth/login` → 200. Redirects to `#/dashboard/dash`. |
| Product listing | 3 products: ADIDAS ORIGINAL $11500, ZARA COAT 3 $11500, iphone 13 pro $55000. Filters: search, price range, categories, sub-categories. "max 9 products per page". Each card: View, Add To Cart. |
| Add to cart | `POST /user/add-to-cart` → 200, navbar badge `Cart 1`. |
| Cart `#/dashboard/cart` | Shows product id, name, MRP, "In Stock", Subtotal and Total ($11500), buttons Buy Now and Checkout. |
| Checkout `#/dashboard/order?prop=[productId]` | Single page, no separate payment page. See form below. |
| Place order | `POST /order/create-order` → **201**, redirects to `#/dashboard/thanks?prop=[orderId]`, toast "Order Placed Successfully". |
| Confirmation | "Thankyou for the order", **order id**, "Click To Download Order Details in CSV", support contact. `GET /order/get-orders-details?id=` is called. |
| Order history `#/dashboard/myorders` | Table: order id, product, price, date, View, Delete. New order listed. |

### Checkout form – inventory
| Field / control | Type | Default | Native constraints | Observed rule |
|---|---|---|---|---|
| Payment method tabs: Credit Card, Paypal, SEPA, Invoice | div tabs | Credit Card active | – | Clicking Paypal does not change the active tab or the form [C]. SEPA / Invoice not individually verified [?]. |
| Credit Card Number | text | pre-filled `4542 9931 9292 2293` | none (no maxlength/pattern/required) | No validation: `abc`, empty and 40 digits all let the order through [C]. |
| Expiry month | select 01–12 | 01 | – | – |
| Expiry year | select 01–31 (2-digit) | 16 | – | Default 01/16 is in the past and **was accepted** [C]. |
| CVV Code | text | empty | none | Empty, `abc`, 12 digits all accepted [C]. |
| Name on Card | text | empty | none | Empty, `12345!@#`, 300 chars all accepted [C]. |
| Apply Coupon + button | text + button | empty | – | Invalid code shows inline `* Invalid Coupon`; no API call seen [C]. Valid coupon unknown [?]. |
| Shipping e-mail | text | logged-in e-mail | none | Empty value not tested [?]. |
| Select Country | autocomplete text | empty | – | Typing `ind` lists British Indian Ocean Territory / India / Indonesia (substring match) [C]. Submit with empty country is **blocked client-side** with toast "Please Enter Full Shipping Information" and no request [C]. |
| Place Order | `<a class="action__submit">` inside `div.actions` | – | – | Click must hit the anchor; a click on the wrapper centre did not submit in MCP. |

### Key API facts
* `create-order` request body is **only** `{"orders":[{"country":"India","productOrderedId":"<id>"}]}` – **card number, expiry, CVV and name are never sent** [C]. Server-side payment validation therefore cannot exist; every payment-field rule is client-side only.
* Response `{"orders":[id],"productOrderId":[id],"message":"Order Placed Successfully"}`.
* `get-orders-details` returns `orderBy` (e-mail), `orderById`, `productName`, `country`, `orderPrice`, `productDescription`.
* When `create-order` fails the UI shows toast "Unknown error occured" and stays on the checkout page.

### Side effects of exploration (documented per instructions)
* **1 real order created** on the shared backend: `6ac909af2be7a4bc2b98b6ef` (ZARA COAT 3, $11500, India, dummy CVV `123`, name `QA Tester`). Account now has 7 orders (6 existed before).
* All later negative probes intercepted and **aborted** `create-order`, so no further orders were created. The cart was left holding ZARA COAT 3 (cart state only).
* Order `Delete` button was not used.

---

## 2. Scenarios

Priority: P0 business critical · P1 high · P2 medium · P3 low.
Common preconditions (unless stated): logged-in user (via API/stored session), cart holds one product, user is on the checkout page, `create-order` is intercepted (record + abort) for negatives so no orders are created.
Common test data: `cvv=123`, `name=QA Tester`, `country=India`, default card `4542 9931 9292 2293`, expiry as listed.
"Existing" = already covered by a test in this repo.

### A. Positive
| ID | Scenario | Rule | Steps | Expected | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|---|
| PAY-001 | Place order with valid dummy data | Valid data creates an order | Fill CVV, name, country (select from list) → Place Order | 201, redirect to thanks page with order id; order id/product match order API | P0 | High – **Existing** `test_placed_order_matches_api_response` (creates a real order) | Order `6ac909af…` created, confirmation shown, history lists it | Confirmed |
| PAY-002 | Country autocomplete suggests and selects | Substring search, selection fills field | Type `ind` → choose India | Options contain India; input = `India` | P2 | High | 3 options for `ind`; selection sets `India` | Confirmed |
| PAY-003 | Checkout summary matches cart | Name, price, quantity carried over | Open checkout from cart | ZARA COAT 3, $11500, Quantity 1 | P1 | High | Matched | Confirmed |
| PAY-004 | New order appears in history for the user | Order belongs to user | After PAY-001 open Orders | Order id listed with product/price; API `orderBy` = test e-mail | P1 | High (read-only once order exists) | Listed; `orderBy=aslamwaqar313@gmail.com` | Confirmed |
| PAY-005 | Confirmation page content | Shows order id, CSV link | After PAY-001 | "Thankyou…" text, id, CSV download link | P2 | Medium | Present | Confirmed |

### B. Required fields
| ID | Scenario | Rule | Test data / steps | Expected (business rule) | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|---|
| PAY-010 | Country blank is blocked | Country required | CVV+name filled, country empty → Place Order | Blocked, toast "Please Enter Full Shipping Information", no request, no order | P0 | High – **Existing** | Blocked, toast shown, no request | Confirmed |
| PAY-011 | CVV blank rejected | CVV required | CVV empty, others valid | Not submitted, error shown | P0 | High – **Existing** (xfail) | **Request sent** (order would be created) | Confirmed – DEFECT |
| PAY-012 | Name on card blank rejected | Name required | Name empty, others valid | Not submitted | P0 | High – **Existing** (xfail) | **Request sent** | Confirmed – DEFECT |
| PAY-013 | Card number blank rejected | Card number required | Card empty, others valid | Not submitted | P0 | High (new) | **Request sent** | Confirmed – DEFECT |
| PAY-014 | Whole form empty is blocked | – | Submit untouched/cleared form | Blocked with shipping toast, no request | P1 | High – **Existing** | Blocked, toast shown | Confirmed |
| PAY-015 | Shipping e-mail blank | E-mail presumably required | Clear e-mail field, submit | Blocked or rejected | P2 | High | Not tested | Requires Investigation |

### C. Input validation
| ID | Scenario | Test data | Expected (business rule) | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|
| PAY-020 | Non-numeric CVV | `abc` | Rejected | P1 | High (xfail) | Field keeps `abc`; **request sent** | Confirmed – DEFECT |
| PAY-021 | Over-long values | card 40×`1`, CVV 12×`9`, name 300×`A` | Rejected / capped | P2 | High (xfail) | **Request sent**, no cap | Confirmed – DEFECT |
| PAY-022 | Malformed card number | `abc` (also covers invalid-format class) | Rejected | P1 | High (xfail) | **Request sent** | Confirmed – DEFECT |
| PAY-023 | Name with digits/symbols | `12345!@#` | Rejected | P2 | High (xfail) | **Request sent** | Confirmed – DEFECT |
| PAY-024 | Whitespace-only CVV / name | `   ` | Rejected | P2 | High | Probe failed on an automation selector, not run | Requires Investigation |

Not scheduled: Luhn-invalid but numeric card numbers – no format rule exists (PAY-022), so a separate test adds nothing until a rule is introduced.

### D. Expiry / date
| ID | Scenario | Test data | Expected | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|
| PAY-030 | Expired card rejected | 01/16 (default) | Rejected | P0 | High (xfail) | **Order created with 01/16** | Confirmed – DEFECT |
| PAY-031 | Expiry dropdown options | – | Months 01–12, years future-only | P2 | High | Months 01–12 ok; years 01–31 include past years | Confirmed – DEFECT (past years offered) |
| PAY-032 | Current month/year boundary | current MM/YY | Accepted | P3 | Medium | Not run; would be accepted by inference since past dates are | Requires Investigation |
| PAY-033 | Invalid month value | e.g. 13 | Rejected | – | – | Dropdown cannot produce it | Not Applicable |

### E. Dropdowns / selections
| ID | Scenario | Steps | Expected | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|
| PAY-040 | Pre-filled defaults | Open checkout | Card number and expiry defaults documented | P3 | High | Card `4542 9931 9292 2293`, 01/16 pre-filled | Confirmed |
| PAY-041 | Alternate payment methods | Click Paypal / SEPA / Invoice | Method switches or shown as unavailable | P2 | High | Paypal: no change [C]; SEPA/Invoice not checked | Requires Investigation |
| PAY-042 | Country not from list | Type `Atlantis`, submit | Rejected | P1 | High (xfail) | **Request sent** with free text; server verdict unknown (aborted) | Requires Investigation (needs mocked/real API probe) |
| PAY-043 | Country typed but not picked | Type `India`, do not pick | Not treated as a selected country | P2 | High | **Corrected in Checkpoint 3:** blocked with the shipping toast, no request. The earlier MCP probe showed "request sent" only because India had already been picked in that session (stale app state). | Confirmed |

### F. Coupon
| ID | Scenario | Test data | Expected | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|
| PAY-050 | Invalid coupon | `INVALID-QA` | Inline error | P2 | High | `* Invalid Coupon`, no API call | Confirmed |
| PAY-051 | Valid coupon | unknown – no coupon code discovered | Discount applied | P3 | – | No known valid code | Requires Investigation |

### G. Submission & error handling
| ID | Scenario | Steps | Expected | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|
| PAY-060 | Rapid repeated submit | Click Place Order 3× | One order only | P1 | Medium – must stub `create-order` with `route.fulfill` (201) to avoid real duplicate orders | 3 requests sent (against an aborted route, so button state unknown) | Requires Investigation |
| PAY-061 | Server error handling | Make `create-order` fail | Error toast, stay on page, cart kept | P1 | High (route abort) | Toast "Unknown error occured", page unchanged | Confirmed |
| PAY-062 | Correct error and resubmit | Fix country after block, submit | Request sent | P1 | High | Request sent after fixing country | Confirmed |

API-level create-order negatives (unknown product, empty list, missing `orders`, no token) are **Existing** in `tests/api/test_create_order_api.py`.

### H. Data integrity & security
| ID | Scenario | Steps | Expected | Pri | Automation | Observed | Status |
|---|---|---|---|---|---|---|---|
| PAY-070 | Card data not sent to the server | Capture create-order body | Body has no card number/CVV/expiry/name | P0 | High (route capture) | Body = country + productOrderedId only | Confirmed |
| PAY-071 | Order belongs to authenticated user | Compare order API `orderById/orderBy` to login user id/e-mail | Match | P1 | High (API) | Matched (`685cb2a0…`) | Confirmed |
| PAY-072 | Order details match placed order | Compare UI/API product, price, country | Match | P1 | High – partially **Existing** | name ZARA COAT 3, price 11500, country India | Confirmed |
| PAY-073 | No card data in Allure / screenshots | Mask card/CVV in attachments | No raw card data in report | P1 | Framework check | Not applicable until tests run | Requires Investigation |

### Summary
Total **33** scenarios: Confirmed 24 (of which 9 confirm defects) · Requires Investigation 8 · Not Applicable 1.
Already covered by existing tests: PAY-001, 010, 011, 012, 014 (+ create-order API negatives). Net-new candidates: 28.

### Defects observed (all client-side validation gaps; no server enforcement exists for payment fields)
1. D-01 Empty CVV accepted (PAY-011)
2. D-02 Empty name on card accepted (PAY-012)
3. D-03 Empty card number accepted (PAY-013)
4. D-04 Non-numeric CVV accepted (PAY-020)
5. D-05 No length limits (PAY-021)
6. D-06 Malformed card number accepted (PAY-022)
7. D-07 Digits/symbols accepted in name (PAY-023)
8. D-08 Expired card (01/16, pre-selected default) accepted (PAY-030)
9. D-09 Expiry year list offers past years (PAY-031)

Practice-app caveat: these may be intentional simplifications of a demo app. They are recorded as defects against the stated business rules and should be tagged `xfail(strict=True)` as the existing suite already does, so a future fix turns the test green and flags the change.

---

### Checkpoint 3 – automation status (run 2026-10-09)
Decisions: defects use `xfail(strict=True)`; PAY-042 and PAY-051 skipped by request.

| Automated (file) | IDs |
|---|---|
| `tests/ui/test_payment_required_fields.py` | PAY-013 (xfail) |
| `tests/ui/test_payment_input_validation.py` | PAY-020, 021 ×3, 022, 023 (all xfail) |
| `tests/ui/test_payment_expiry.py` | PAY-031 months (pass), PAY-031 years (xfail), PAY-030 (xfail) |
| `tests/ui/test_payment_methods_country_coupon.py` | PAY-003, 040, 002, 043, 050 (pass) |
| `tests/ui/test_payment_submission.py` | PAY-061, 062, 070 (pass) |
| `tests/api/test_order_ownership_api.py` | PAY-071, 072 (pass) |
| Pre-existing | PAY-001, 010, 011, 012, 014 |

Not automated: PAY-004, 005 (need another real order), 015, 024, 032, 041, 060, 073 (Requires Investigation), 042 and 051 (skipped by decision), 033 (N/A).

## 3. Proposed Page Object Model (for approval – Checkpoint 2)

The app uses one combined checkout/payment page, so **no new `PaymentPage`** is needed. Reuse and extend existing classes.

| Class | Change | Responsibility |
|---|---|---|
| `LoginPage`, `DashboardPage`, `CartPage` | none | existing |
| `CheckoutPage` (extend) | add locators: `card_number`, `expiry_month`, `expiry_year`, `coupon_input`, `coupon_button`, `coupon_error`, `payment_tabs`, `shipping_email`, `country_options`; point `place_order_button` at `a.action__submit`; methods `fill_card(...)`, `select_expiry(m, y)`, `choose_country(name)`, `type_country_without_selecting(text)`, `apply_coupon(code)`, `order_summary()`, `read_card_form_values()`; keep `capture_order_requests()` and add `stub_order_success()` (`route.fulfill` 201) | locators + interactions only |
| `OrderConfirmationPage` (extend) | `order_id()`, `csv_link` | existing class |
| `OrderHistoryPage` | none | existing |

**Tests** (business assertions only, in `tests/ui/`):
* `test_payment_required_fields.py` – PAY-010…015 (defect cases `xfail(strict=True)`)
* `test_payment_input_validation.py` – PAY-020…024 (parametrised)
* `test_payment_expiry.py` – PAY-030…032
* `test_payment_methods_and_country.py` – PAY-002, 040…043, 050
* `test_payment_submission.py` – PAY-060…062 (stubbed backend, no real orders)
* `tests/e2e/` – PAY-001/004/005 stay in the existing e2e test (single real order per run)
* `tests/api/` – PAY-070/071/072 using the `api` fixture and captured request body

**Fixtures / data / config**
* `conftest.py`: add `order_requests` fixture (captures and aborts create-order), `checkout_page` (cart seeded through the API, as the existing `checkout` fixture does).
* `test_data/payment.json`: dummy card, CVV, names, boundary strings, expiry cases. Dummy data only.
* Credentials stay in `.env` via `config/settings.py`; nothing hard-coded.
* Allure: titles/steps on each test; a `mask_card()` helper in `utils/` so any attached text/screenshot hides card number/CVV.

**Order policy:** only PAY-001 places a real order (one per full run). All other submission tests abort or stub `create-order`.

## 4. Open questions for you
1. Should defect scenarios be automated as `xfail(strict=True)` (current repo convention)? Recommended: yes.
2. OK to run PAY-042 (free-text country) against the real API once, creating at most one extra order, to learn the server verdict?
3. Is a valid coupon code known? Otherwise PAY-051 stays un-automated.
