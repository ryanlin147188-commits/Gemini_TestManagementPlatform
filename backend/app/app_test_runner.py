"""
app_test_runner.py
==================

This module contains a pytest test suite for executing mobile app UI
automation based on JSON-encoded test case definitions. It uses Appium
to interact with Android or iOS devices/emulators.

**IMPORTANT PRE-REQUISITES FOR USER:**
1.  **Appium Server:** An Appium 2.0 server must be running and accessible.
2.  **Appium Drivers:** The appropriate drivers must be installed (e.g., `appium driver install uiautomator2` for Android).
3.  **Emulator/Simulator:** An Android emulator or iOS simulator must be running.
4.  **App File:** The .apk or .ipa file must be placed in the `data/` directory.

Environment variables
---------------------

- `APP_TEST_CASES_FILE`: Path to the JSON file with test cases for the selected project.
- `PROJECT_ID`: The ID of the project whose cases will be run.
- `APP_ELEMENTS_FILE`: Path to the JSON file mapping logical element names to Appium locators.
- `APP_FILE_NAME`: The filename of the .apk or .ipa file in the `data/` directory (e.g., `my-app.apk`).
- `PLATFORM_NAME`: "Android" or "iOS".
- `PLATFORM_VERSION`: The OS version of the device/emulator (e.g., "13.0").
- `DEVICE_NAME`: The name of the device/emulator (e.g., "Android Emulator" or "iPhone 14").
- `APPIUM_SERVER_URL`: The URL of the running Appium server (defaults to http://127.0.0.1:4723).
"""

from __future__ import annotations

import os
import json
import pytest
from typing import Dict, List, Any, Tuple

import allure
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import WebDriverException

# --- Helper Functions ---

def _load_json_file(path: str | None) -> Dict:
    """Loads a JSON file and returns its content. Returns empty dict if path is None or file not found."""
    if not path or not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def _load_app_elements() -> Dict[str, Dict[str, str]]:
    """Load the element mapping from the APP_ELEMENTS_FILE."""
    path = os.getenv("APP_ELEMENTS_FILE")
    return _load_json_file(path)

def _load_test_cases() -> Dict[str, List[Dict[str, Any]]]:
    """Load and group test cases by 'test_feature' for the selected project."""
    cases_file = os.getenv("APP_TEST_CASES_FILE")
    project_id = os.getenv("PROJECT_ID", "1")
    data = _load_json_file(cases_file)

    project_cases: List[Dict[str, Any]] = data.get(str(project_id), [])
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for entry in project_cases:
        case = dict(entry)
        feature = case.get("test_feature") or case.get("feature") or "Unnamed Feature"
        case["test_feature"] = feature
        grouped.setdefault(str(feature), []).append(case)

    for feature_name, steps in grouped.items():
        try:
            grouped[feature_name] = sorted(steps, key=lambda x: int(x.get("test_step") or 0))
        except (ValueError, TypeError):
            pass  # Keep original order if step is not a valid integer

    return grouped

def _collect_cases() -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Retrieve grouped cases for parameterization."""
    cases_by_feature = _load_test_cases()
    return list(cases_by_feature.items())

# Prepare cases and IDs for pytest to fix Chinese character display in reports
_collected_app_cases = _collect_cases()
_app_case_ids = [item[0] for item in _collected_app_cases]


# --- Appium and Pytest Fixtures ---

@pytest.fixture(scope="session")
def appium_driver():
    """Provides an Appium driver for the entire test session."""
    options = AppiumOptions()
    platform_name = os.getenv("PLATFORM_NAME", "Android")

    # --- USER CONFIGURABLE ---
    # These capabilities may need to be adjusted to match the local test environment.
    options.set_capability("platformName", platform_name)
    options.set_capability("platformVersion", os.getenv("PLATFORM_VERSION", "13.0"))
    options.set_capability("deviceName", os.getenv("DEVICE_NAME", "Android Emulator"))

    app_file_name = os.getenv("APP_FILE_NAME")
    if app_file_name:
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", app_file_name))
        options.set_capability("app", app_path)

    if platform_name.lower() == "android":
        options.set_capability("automationName", "UiAutomator2")
    elif platform_name.lower() == "ios":
        options.set_capability("automationName", "XCUITest")

    server_url = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

    driver = None
    try:
        driver = webdriver.Remote(server_url, options=options)
        yield driver
    finally:
        if driver:
            driver.quit()

# --- Test Execution Logic ---

def _find_element(driver, selector_info: Dict[str, str]):
    """Finds an element using the locator strategy and value from selector_info."""
    strategy = selector_info.get("strategy", "").lower()
    value = selector_info.get("value", "")

    by_map = {
        "id": AppiumBy.ID,
        "xpath": AppiumBy.XPATH,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "class_name": AppiumBy.CLASS_NAME,
        "name": AppiumBy.NAME,
    }

    if strategy not in by_map:
        raise ValueError(f"Unsupported locator strategy: {strategy}")

    return driver.find_element(by=by_map[strategy], value=value)

def _perform_action(driver, action: str, element, value: str | None) -> None:
    """Dispatches the appropriate Appium call based on the action name."""
    action = action.lower()
    if action in ("填入", "fill", "send_keys"):
        if element:
            element.send_keys(value or "")
    elif action in ("點擊", "click"):
        if element:
            element.click()
    elif action in ("等待", "wait"):
        timeout_ms = 1000
        try:
            if value:
                timeout_ms = int(float(value))
                if timeout_ms < 100: # Assume seconds if value is small
                    timeout_ms *= 1000
        except (ValueError, TypeError):
            pass
        driver.implicitly_wait(timeout_ms / 1000) # Appium wait is in seconds
    else:
        # Silently ignore unknown actions
        pass

def _attach_screenshot(driver, name: str):
    """Captures a screenshot and attaches it to the Allure report."""
    try:
        img_bytes = driver.get_screenshot_as_png()
        allure.attach(img_bytes, name=name, attachment_type=allure.attachment_type.PNG)
    except WebDriverException:
        pass # Ignore screenshot errors

def _run_steps(driver, steps: List[Dict[str, Any]], ui_map: Dict[str, Any], feature: str) -> None:
    """Executes a series of test steps."""
    for step in steps:
        action = step.get("action", "")
        description = step.get("description") or step.get("desc") or ""
        test_step = step.get("test_step")
        step_name = f"{test_step}: {description or action}" if test_step else (description or action)

        element_key = step.get("element") or ""
        value = step.get("value") or ""

        element = None

        with allure.step(step_name):
            _attach_screenshot(driver, f"{feature}_step{test_step}_before")
            try:
                if element_key and ui_map.get(element_key):
                    selector_info = ui_map[element_key]
                    element = _find_element(driver, selector_info)

                _perform_action(driver, action, element, value)

            except Exception as e:
                _attach_screenshot(driver, f"{feature}_step{test_step}_error")
                pytest.fail(f"Error in step '{step_name}': {e}")

            _attach_screenshot(driver, f"{feature}_step{test_step}_after")

# --- Pytest Entry Point ---

@pytest.mark.parametrize("feature, steps", _collected_app_cases, ids=_app_case_ids)
def test_app_cases(appium_driver, feature: str, steps: List[Dict[str, Any]]) -> None:
    """Pytest entry point for APP UI cases."""
    ui_map = _load_app_elements()
    _run_steps(appium_driver, steps, ui_map, feature)
