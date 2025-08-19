"""
api_test_runner.py
===================

This module defines a pytest test suite for executing API test cases
based on JSON definitions. Like the web UI runner, it is intended to be
invoked by the backend when a user triggers an "API 立即測試" action. The
runner reads a JSON file specified via the ``API_TEST_CASES_FILE``
environment variable. The file maps project IDs to lists of test step
dictionaries. Each step can define request parameters and expectations.

Environment variables
---------------------

``API_TEST_CASES_FILE``: Path to a JSON file containing scoped API test
cases. The file should be structured as ``{ project_id: [case, case,...] }``.

``PROJECT_ID``: Numeric project identifier (string accepted). Only
cases matching this ID will be executed.

``REQUEST_TIMEOUT``: Optional integer specifying the request timeout
in seconds. Defaults to 10 seconds if unset or invalid.

Case definition
---------------

Each case dictionary may contain the following keys:

* ``test_feature`` or ``feature``: Name of the test scenario. Cases with
  the same feature are grouped into a single pytest test function.
* ``test_step`` or ``step``: Step number within the scenario. Used for
  ordering and included in the Allure step name.
* ``method``: HTTP method (GET, POST, PUT, DELETE, etc.). Defaults to
  ``GET`` if missing.
* ``url``: Base URL to which the request is sent.
* ``api_path``: Additional path appended to ``url``. Both fields are
  concatenated to form the full endpoint.
* ``header``: JSON string defining request headers. Can be empty or
  omitted.
* ``body``: JSON string defining the request payload. Used for POST,
  PUT, etc. Can be empty or omitted.
* ``expected_status``: Expected HTTP status code as a string.
* ``expected_field``: Dot‑notation path to a value within the JSON
  response. Supports simple nested objects and array indexing (e.g.
  ``data.items[0].name``). Can be omitted to skip body assertions.
* ``expected_value``: The expected value at ``expected_field`` in the
  response body. Compared as a string. Ignored if ``expected_field`` is
  not provided.
* ``description`` or ``desc``: Optional description of the step. Used in
  the Allure step name.

During execution, the runner will attach the request details and
response text to the Allure report before asserting status and body
conditions. Any failures will cause the test to fail and be reported.
"""

from __future__ import annotations

import os
import json
import ast
from typing import Dict, List, Any, Tuple

import pytest  # type: ignore
import allure  # type: ignore
import httpx  # type: ignore


def _load_test_cases() -> Dict[str, List[Dict[str, Any]]]:
    """Load and normalise API test cases from the file specified by
    ``API_TEST_CASES_FILE`` for the selected project.

    The returned mapping groups cases by their ``test_feature`` (falling
    back to ``feature`` or ``Unnamed``). Each case dictionary is copied
    and fields ``test_feature``, ``test_step``, ``description`` are
    normalised. This function tolerates missing keys by supplying
    sensible defaults. If no cases are found, an empty dict is returned.
    """
    path = os.getenv("API_TEST_CASES_FILE")
    project_id = os.getenv("PROJECT_ID", "1")
    if not path or not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    cases = data.get(str(project_id), [])
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in cases:
        case = dict(entry)
        feature = case.get("test_feature") or case.get("feature") or "Unnamed"
        case["test_feature"] = feature
        step = case.get("test_step") or case.get("step") or 0
        case["test_step"] = step
        if "description" not in case and case.get("desc"):
            case["description"] = case.get("desc")
        grouped.setdefault(str(feature), []).append(case)
    # sort each group by integer test_step
    for feature_name, steps in grouped.items():
        try:
            grouped[feature_name] = sorted(
                steps,
                key=lambda x: int(x.get("test_step") or 0),
            )
        except Exception:
            grouped[feature_name] = steps
    return grouped


def _collect_cases() -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Convert the grouped cases dict into a list of (feature, steps) tuples
    for parametrisation. If no cases exist, an empty list is returned.
    """
    cases_by_feature = _load_test_cases()
    return [(feature, steps) for feature, steps in cases_by_feature.items()]


# Prepare cases and their IDs for pytest parametrization. This is done at the
# module level to avoid calling _collect_cases() multiple times.
_collected_api_cases = _collect_cases()
_api_case_ids = [item[0] for item in _collected_api_cases]


def _get_timeout() -> int:
    """Retrieve the request timeout in seconds from the environment.
    Defaults to 10 seconds if unset or invalid.
    """
    try:
        return int(os.getenv("REQUEST_TIMEOUT", "10"))
    except Exception:
        return 10


def _parse_json_maybe(text: str) -> dict:
    """Parse a JSON‑like string into a dictionary.

    Attempts to parse the string first as JSON and, if that fails,
    falls back to Python literal evaluation. Single quotes will be
    accepted via ``ast.literal_eval``. If parsing fails or the
    result is not a dictionary, an empty dict is returned.
    """
    if not text or not text.strip():
        return {}
    try:
        # Attempt to load as strict JSON
        return json.loads(text)
    except Exception:
        # Replace single quotes with double quotes as a simple heuristic
        # and try JSON again; this won't handle nested mismatched quotes
        try:
            candidate = text.replace("'", '"')
            return json.loads(candidate)
        except Exception:
            pass
    try:
        # Fallback: use literal_eval to handle Python dict syntax
        result = ast.literal_eval(text)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _get_nested_value(data: Any, path: str) -> str:
    """Traverse a nested dictionary/list structure using dot notation.

    Supports array indexing via square brackets, e.g. ``items[0].name``.
    Returns the value converted to string if found; otherwise returns an
    empty string.
    """
    try:
        current = data
        for part in path.split('.'):
            if '[' in part and ']' in part:
                # handle simple array indexing, e.g. items[0]
                key, rest = part.split('[', 1)
                index_str = rest.split(']')[0]
                idx = int(index_str)
                current = current[key][idx]
            else:
                current = current[part]
        return str(current)
    except Exception:
        return ""


def _run_steps(client: httpx.Client, steps: List[Dict[str, Any]], feature: str) -> None:
    """Execute a sequence of API test steps. Each step sends an HTTP request
    and asserts the expected status and body values. Request and response
    information are attached to the Allure report.
    """
    timeout = _get_timeout()
    for step in steps:
        method = str(step.get("method", "GET")).upper()
        base_url = str(step.get("url", ""))
        api_path = str(step.get("api_path", ""))
        # Construct the full request URL. Ensure there is exactly one slash
        # between ``base_url`` and ``api_path`` when both are present. If
        # ``base_url`` is empty, use ``api_path`` as is.
        if base_url:
            if base_url.endswith('/') and api_path.startswith('/'):
                url = base_url.rstrip('/') + api_path
            elif not base_url.endswith('/') and not api_path.startswith('/'):
                url = base_url + '/' + api_path
            else:
                url = base_url + api_path
        else:
            url = api_path
        headers_str = step.get("header") or step.get("headers") or ""
        body_str = step.get("body") or step.get("payload") or ""
        headers = _parse_json_maybe(headers_str)
        body = _parse_json_maybe(body_str)
        # expected status/field/value: support older keys with short names
        expected_status = str(
            step.get("expected_status")
            or step.get("expected_code")
            or step.get("expect_status")
            or step.get("expect_code")
            or "200"
        )
        expected_field = (
            step.get("expected_field")
            or step.get("expected_key")
            or step.get("expect_field")
            or step.get("expect_key")
            or ""
        )
        expected_value = (
            step.get("expected_value")
            or step.get("expected_val")
            or step.get("expect_value")
            or step.get("expect_val")
            or ""
        )
        description = step.get("description") or step.get("desc") or ""
        test_step = step.get("test_step") or step.get("step") or ""
        step_name = f"{test_step}: {description or method} {api_path}" if test_step else (description or method)
        with allure.step(step_name):
            # Attach request details before sending
            request_details = {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
            }
            allure.attach(
                json.dumps(request_details, ensure_ascii=False, indent=2).encode("utf-8"),
                name=f"{feature}_step{test_step}_request",
                attachment_type=allure.attachment_type.JSON,
            )
            try:
                # Send the HTTP request
                response = client.request(method, url, headers=headers, json=body if body else None, timeout=timeout)
            except Exception as e:
                # Attach error and rethrow
                allure.attach(
                    str(e).encode("utf-8"),
                    name=f"{feature}_step{test_step}_error",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise
            # Attach response body
            try:
                resp_text = response.text
            except Exception:
                resp_text = ""
            allure.attach(
                resp_text.encode("utf-8"),
                name=f"{feature}_step{test_step}_response",
                attachment_type=allure.attachment_type.TEXT,
            )
            # Assert status code
            assert str(response.status_code) == expected_status, (
                f"期望狀態碼 {expected_status}, 實際為 {response.status_code}"
            )
            # If no expected field is defined, skip body assertions
            if expected_field:
                try:
                    resp_json = response.json()
                except Exception:
                    pytest.fail("回應不是有效的 JSON")
                actual_value = _get_nested_value(resp_json, expected_field)
                assert actual_value == str(expected_value), (
                    f"期望欄位 {expected_field} 的值為 {expected_value}, 實際為 {actual_value}"
                )


@pytest.fixture(scope="session")
def http_client() -> httpx.Client:
    """Provide a single HTTP client instance for all tests in this session."""
    with httpx.Client() as client:
        yield client


@pytest.mark.parametrize("feature, steps", _collected_api_cases, ids=_api_case_ids)
def test_api_cases(http_client: httpx.Client, feature: str, steps: List[Dict[str, Any]]) -> None:
    """Pytest entry point for API cases. Each feature becomes a test
    function. All defined steps for that feature are executed sequentially.
    Failures propagate up to pytest/Allure for reporting.
    """
    _run_steps(http_client, steps, feature)