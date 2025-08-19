"""
web_test_runner.py
===================

This module contains a simple pytest test suite for executing web UI
automation based on JSON‑encoded test case definitions. It is designed to
integrate with the existing test platform backend. The tests are written
using Playwright and Allure to capture rich execution details including
before/after screenshots for every action.

Environment variables
---------------------

The behaviour of this test runner is governed by a few environment
variables which are typically set by the backend before spawning pytest:

```
WEB_TEST_CASES_FILE  Path to a JSON file containing web test cases. The
                     file should map project IDs to a list of case
                     dictionaries. Each case dictionary must include the
                     following keys:

                     - ``test_feature``: Name or identifier of the test
                       scenario. Cases with the same feature will be
                       grouped into a single test function.
                     - ``test_step``: Step number within the scenario.
                     - ``action``: Action to perform. Supported values
                       include ``前往網址`` (navigate), ``填入`` (fill),
                       ``點擊`` (click), ``選擇`` (select), ``等待``
                       (wait for milliseconds), ``檢查`` (assert
                       visibility) and ``檔案上傳`` (upload).
                     - ``element``: Logical key corresponding to a UI
                       element. This key will be resolved using the
                       mapping defined in ``UI_ELEMENTS_FILE``. If a key
                       is not found in the mapping, it will be treated as
                       a raw selector.
                     - ``value``: Optional value used by certain actions
                       (e.g. URL for navigation, text to enter, option
                       value to select, file path to upload or wait
                       timeout in milliseconds for ``等待``).
                     - ``description``: Optional description of the step.

PROJECT_ID          Numeric project identifier. Only cases matching this
                     ID will be executed.

UI_ELEMENTS_FILE    Path to a JSON file mapping logical element keys
                     (used in ``element``) to CSS selectors understood by
                     Playwright.

The backend will generate a temporary JSON file containing only the
selected test cases and set the appropriate environment variables before
invoking pytest on this module.
"""

from __future__ import annotations

import os
import json
import pytest
from typing import Dict, List, Any, Tuple

import allure  # type: ignore
from playwright.sync_api import sync_playwright, Page  # type: ignore


def _load_ui_elements() -> Dict[str, str]:
    """Load the element mapping from a JSON file specified by the
    ``UI_ELEMENTS_FILE`` environment variable. If the file cannot be
    loaded, an empty mapping is returned. This function centralises the
    lookup so that missing or corrupted files do not crash the test run.
    """
    path = os.getenv("UI_ELEMENTS_FILE")
    if not path or not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # ensure all keys and values are strings
        return {str(k): str(v) for k, v in data.items()}
    except Exception:
        return {}


def _load_test_cases() -> Dict[str, List[Dict[str, Any]]]:
    """Load and group test cases by ``test_feature`` for the selected
    project. The cases file is specified via the ``WEB_TEST_CASES_FILE``
    environment variable. The selected project is determined by
    ``PROJECT_ID``. The returned dictionary maps feature names to
    lists of step dictionaries sorted by the ``test_step`` field.

    This loader is tolerant of different field naming conventions. If a
    case dictionary lacks the expected ``test_feature`` or ``test_step`` keys,
    it will fall back to ``feature`` and ``step`` respectively. Likewise,
    ``description`` will fall back to ``desc`` when not present. A copy of
    each case is normalised before grouping so that downstream code
    consistently reads ``test_feature``, ``test_step``, ``description``,
    ``action``, ``element`` and ``value`` keys. Missing numeric step values
    default to ``0`` for sorting purposes. If the JSON file or the project
    entry is missing, an empty dict is returned.
    """
    cases_file = os.getenv("WEB_TEST_CASES_FILE")
    project_id = os.getenv("PROJECT_ID", "1")
    if not cases_file or not os.path.isfile(cases_file):
        return {}
    try:
        with open(cases_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    # retrieve cases for this project id; expecting a list of dicts
    project_cases: List[Dict[str, Any]] = data.get(str(project_id), [])
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in project_cases:
        # work on a copy so we don't mutate the original dictionary
        case = dict(entry)
        # normalise the feature name; fall back to ``feature`` or 'Unnamed'
        feature = case.get("test_feature") or case.get("feature") or "Unnamed"
        case["test_feature"] = feature
        # normalise the step number; fall back to ``step`` or 0
        step_val = case.get("test_step") or case.get("step") or 0
        case["test_step"] = step_val
        # normalise the description; fall back to ``desc`` if provided
        if "description" not in case and case.get("desc"):
            case["description"] = case.get("desc")
        # ensure ``action``, ``element`` and ``value`` keys exist
        case.setdefault("action", case.get("action"))
        case.setdefault("element", case.get("element"))
        case.setdefault("value", case.get("value"))
        # group by feature
        grouped.setdefault(str(feature), []).append(case)
    # sort each group by numeric test_step if present
    for feature_name, steps in grouped.items():
        try:
            grouped[feature_name] = sorted(
                steps,
                key=lambda x: int(x.get("test_step") or 0),
            )
        except Exception:
            # if conversion fails, keep original order
            grouped[feature_name] = steps
    return grouped


# Fixture definitions for Playwright
@pytest.fixture(scope="session")
def browser_context():
    """Launch a single browser instance for all tests in this session.
    A new context is created by each test function via the ``page`` fixture.
    """
    with sync_playwright() as p:
        # Use Chromium by default; other browsers could be selected here
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Provide a fresh browser context and page for each test. Playwright
    contexts ensure isolation of cookies, local storage and other state.
    The viewport is standardised for consistent screenshots.
    """
    context = browser_context.new_context()
    _page = context.new_page()
    _page.set_viewport_size({"width": 1920, "height": 1080})
    yield _page
    context.close()


def _perform_action(page: Page, action: str, selector: str | None, value: str | None) -> None:
    """Dispatch the appropriate Playwright call based on the action name.
    Unsupported actions are ignored. Errors will propagate to pytest and be
    recorded by Allure. The mapping uses Chinese action names that align
    with the UI test definitions.

    :param page: Playwright page object
    :param action: Name of the action (e.g. '點擊', '填入', etc.)
    :param selector: Resolved CSS selector; may be None for actions that
                     do not require a target element (e.g. navigation)
    :param value: Optional value used by certain actions
    """
    if action in ("前往網址", "navigate", "goto"):
        if value:
            page.goto(value)
    elif action in ("填入", "填寫", "input", "fill"):
        if selector:
            page.locator(selector).fill(value or "")
    elif action in ("點擊", "點選", "click"):
        if selector:
            page.locator(selector).click()
    elif action in ("選擇", "select"):
        if selector:
            page.locator(selector).select_option(value or "")
    elif action in ("等待", "wait"):
        # Accept numeric value in milliseconds or seconds
        try:
            # If provided value looks like seconds (e.g. '5'), convert to ms
            timeout_ms = int(float(value))
            # interpret values less than 100 as seconds for user convenience
            if timeout_ms < 100:
                timeout_ms *= 1000
            page.wait_for_timeout(timeout_ms)
        except Exception:
            # default wait of 1 second
            page.wait_for_timeout(1000)
    elif action in ("檢查", "assert", "check"):
        if selector:
            page.locator(selector).wait_for(timeout=5000)
    elif action in ("檔案上傳", "upload"):
        if selector and value:
            page.locator(selector).set_input_files(value)
    else:
        # Unknown actions are ignored to avoid breaking the test run
        pass


def _attach_screenshot(page: Page, name: str) -> None:
    """Capture a full‑page PNG screenshot and attach it to the Allure
    report. If screenshot capture fails, the exception is silently
    swallowed so as not to interrupt the test flow.
    """
    try:
        img_bytes = page.screenshot(full_page=True)
        allure.attach(
            img_bytes,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        # Do not raise errors from screenshot capture
        pass


def _resolve_selector(ui_map: Dict[str, str], element_key: str | None) -> str | None:
    """Resolve a logical element key to a concrete selector. If the key
    exists in the UI mapping, return the mapped selector. Otherwise,
    return the key itself (useful when a raw selector is stored directly
    in the case definition). Empty strings and None values yield None.
    """
    if not element_key:
        return None
    selector = ui_map.get(str(element_key))
    if selector:
        return selector
    # fallback: treat the element key itself as a selector
    return str(element_key)


def _run_steps(page: Page, steps: List[Dict[str, Any]], ui_map: Dict[str, str], feature: str) -> None:
    """Execute a series of test steps within a single test function. Each
    step is wrapped in an Allure step context to record its name and
    associate attachments with it. Screenshots of the page are captured
    before and after every action.
    """
    for step in steps:
        action = step.get("action") or ""
        description = step.get("description") or ""
        test_step = step.get("test_step")
        step_name = f"{test_step}: {description or action}" if test_step is not None else (description or action)
        element_key = step.get("element") or ""
        value = step.get("value") or ""
        selector = _resolve_selector(ui_map, element_key)
        with allure.step(step_name):
            # Screenshot before performing the action
            _attach_screenshot(page, f"{feature}_step{test_step}_before")
            # Perform the UI action
            try:
                _perform_action(page, action, selector, value)
            except Exception:
                # Capture a screenshot on error before propagating
                _attach_screenshot(page, f"{feature}_step{test_step}_error")
                raise
            # Screenshot after performing the action
            _attach_screenshot(page, f"{feature}_step{test_step}_after")


def _collect_cases() -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Retrieve grouped cases and convert them into a list of tuples for
    parameterisation. Each tuple consists of the feature name and its
    associated list of steps.
    """
    cases_by_feature = _load_test_cases()
    return [(feature, steps) for feature, steps in cases_by_feature.items()]


# Prepare cases and their IDs for pytest parametrization. This is done at the
# module level to avoid calling _collect_cases() multiple times.
_collected_web_cases = _collect_cases()
_web_case_ids = [item[0] for item in _collected_web_cases]


@pytest.mark.parametrize("feature, steps", _collected_web_cases, ids=_web_case_ids)
def test_web_cases(page: Page, feature: str, steps: List[Dict[str, Any]]) -> None:
    """Pytest entry point for web UI cases. The test name will be the
    feature name, and within the test each defined step is executed in
    sequence. Any exceptions thrown during step execution will fail the
    test and be reported by pytest/Allure.
    """
    ui_map = _load_ui_elements()
    _run_steps(page, steps, ui_map, feature)