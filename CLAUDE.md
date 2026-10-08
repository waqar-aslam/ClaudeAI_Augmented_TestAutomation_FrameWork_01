# QA Automation Project

## Project Purpose

This is a Python-based UI and API test automation framework.

The framework uses:

- Python
- Pytest
- Playwright
- Page Object Model
- Allure Reports

The project will eventually use Claude Code as an AI-assisted QA automation agent.

---

# Technology Stack

- Language: Python
- Test Framework: Pytest
- UI Automation: Playwright
- API Testing: Playwright APIRequestContext
- Design Pattern: Page Object Model
- Reporting: Allure
- Package Management: pip
- IDE: PyCharm

---

# Project Structure

tests/
    Contains test cases.

pages/
    Contains Page Object classes.

utils/
    Contains reusable utilities and helper functions.

test_data/
    Contains test data.

conftest.py
    Contains Pytest fixtures.

allure-results/
    Contains raw Allure test results.

---

# Automation Rules

Use Page Object Model for UI automation.

Do not put large amounts of locator or UI interaction logic directly inside test files.

Tests should describe business behavior.

Page objects should contain:

- Locators
- Page interactions
- Page-specific validation helpers

---

# Playwright Rules

Use Playwright synchronization mechanisms.

Do NOT use unnecessary hard waits such as:

page.wait_for_timeout()

Prefer:

- locator.wait_for()
- expect()
- Playwright auto-waiting
- network synchronization when appropriate

Avoid fragile XPath selectors when better selectors are available.

Prefer:

- get_by_role()
- get_by_label()
- get_by_text()
- get_by_test_id()

---

# Pytest Rules

Use fixtures for reusable setup.

Tests must be independent.

Do not make tests dependent on execution order.

Use meaningful test names.

Example:

test_user_can_add_product_to_cart()

is preferred over:

test_case_01()

---

# API Validation

When UI data originates from an API, prefer validating important UI information against the API response.

For example:

API response
    ↓
Order ID
Product name
Price

should be compared with:

UI
    ↓
Order ID
Product name
Price

---

# Allure Rules

Use meaningful Allure titles.

Use Allure steps for important business actions.

Example:

@allure.step("Login as valid user")

Use attachments when useful for debugging failures.

---

# Test Execution

Default command:

pytest

Allure results:

pytest --alluredir=allure-results

---

# Claude Code Rules

Before making significant changes:

1. Understand the existing project.
2. Explain the proposed approach.
3. Make the smallest appropriate change.
4. Run the affected tests.
5. Analyze failures.
6. Do not modify application code unless explicitly requested.

Never create fake test results.

Never claim a test passed unless it was actually executed.

When a test fails, determine whether the likely cause is:

- Application defect
- Automation defect
- Environment issue
- Test-data issue

---

# QA Principles

Think like a Senior QA Automation Engineer.

For every requirement consider:

- Positive scenarios
- Negative scenarios
- Boundary conditions
- Validation rules
- Error handling
- API validation
- UI validation
- Regression impact
- Test data requirements

Do not blindly automate every scenario.

Prioritize business-critical scenarios.