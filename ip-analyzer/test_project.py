"""
IP Analyzer - Test Suite

This module contains unit tests for the IP extraction and input validation logic.
Since 'sys.argv' and the file system are external dependencies, we use 'monkeypatch'
and 'tmp_path' fixtures to simulate (mock) command-line arguments and file
interactions. This prevents 'sys.exit' from terminating the test runner and
ensures a clean, isolated testing environment.
"""

import sys
import json
import pytest
from pathlib import Path
import time
import requests
from unittest.mock import Mock
from project import (
    validate_input,
    _extract_from_regex,
    _extract_from_json,
    ip_info,
    get_ip_details,
)

# -----------------------------------------------------------------------------
# Extraction Logic Tests
# -----------------------------------------------------------------------------


def test_extract_from_regex_valid():
    """Tests if valid IPs are extracted and duplicates are removed."""
    text = "Check 192.168.1.1 and 8.8.8.8. Duplicate: 192.168.1.1"
    result = _extract_from_regex(text)
    assert len(result) == 2
    assert "192.168.1.1" in result
    assert "8.8.8.8" in result


def test_extract_from_regex_invalid_octets():
    """Tests that octets above 255 are rejected."""
    text = "Invalid IPs: 256.0.0.1, 123.456.78.9"
    assert _extract_from_regex(text) == []


def test_extract_from_json_valid():
    """Tests extraction from a valid JSON structure regardless of keys."""
    json_data = '{"server": "10.0.0.1", "clients": ["192.168.0.50", "172.16.0.1"]}'
    result = _extract_from_json(json_data)
    assert len(result) == 3
    assert "10.0.0.1" in result
    assert "192.168.0.50" in result


# -----------------------------------------------------------------------------
# Input Validation Tests
# -----------------------------------------------------------------------------


def test_validate_input_success(monkeypatch, tmp_path):
    """Verifies successful path return when arguments and file are correct."""
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "logs.txt"
    f.write_text("testing text ttttt")

    monkeypatch.setattr(sys, "argv", ["project.py", str(f)])
    result = validate_input()
    assert isinstance(result, Path)
    assert result.name == "logs.txt"


def test_validate_input_no_args(monkeypatch):
    """Verifies SystemExit when no filename is provided."""
    monkeypatch.setattr(sys, "argv", ["project.py"])
    with pytest.raises(SystemExit) as excinfo:
        validate_input()
    assert "Too few" in str(excinfo.value)


def test_validate_input_unsupported_extension(monkeypatch, tmp_path):
    """Verifies SystemExit for unsupported extension."""
    f = tmp_path / "report.pdf"
    f.write_text("testing text ttttt")

    monkeypatch.setattr(sys, "argv", ["project.py", str(f)])
    with pytest.raises(SystemExit) as excinfo:
        validate_input()
    assert "Unsupported file type" in str(excinfo.value)


# -----------------------------------------------------------------------------
# Orchestration Test (ip_info)
# -----------------------------------------------------------------------------


def test_ip_info_routing(tmp_path):
    """Tests if ip_info correctly routes to JSON or Regex based on extension."""
    # Test JSON routing
    json_file = tmp_path / "data.json"
    json_file.write_text('{"ip": "1.1.1.1"}')
    assert ip_info(json_file) == ["1.1.1.1"]

    # Test Plain Text routing
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("IP is 2.2.2.2")
    assert ip_info(txt_file) == ["2.2.2.2"]


# -----------------------------------------------------------------------------
# API Tests
# -----------------------------------------------------------------------------


def test_get_ip_details_batching(monkeypatch):
    """
    Tests if the function correctly slices the IP list into batches
    and aggregates results from multiple API calls.
    """

    # 1. Config: Creates a list of 120 IPs (test batches of 50)
    mock_ips = [f"1.1.1.{i}" for i in range(120)]

    # 2. Mock API response:
    # Testing .requests
    def mock_post(url, json=None):
        response = Mock()
        response.status_code = 200
        # Simulate that the API returns a list of dictionaries with the IPs sent
        response.json.return_value = [
            {"query": item["query"], "status": "success"} for item in json
        ]
        return response

    # Replaced the actual requests.post
    monkeypatch.setattr(requests, "post", mock_post)

    # 3. Mock time.sleep:
    sleep_counter = Mock()
    monkeypatch.setattr(time, "sleep", sleep_counter)

    # 4. Execution
    results = get_ip_details(mock_ips)

    # Checked that all 120 IPs came back in the final report
    assert len(results) == 120
    assert results[0]["query"] == "1.1.1.0"
    assert results[-1]["query"] == "1.1.1.119"

    # Checked Rate Limiting:
    # For 120 IPs 50 each batch we have 3 requests
    assert sleep_counter.call_count == 2
