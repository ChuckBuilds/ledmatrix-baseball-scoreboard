#!/usr/bin/env python3
"""
Test script for LED Matrix Web Interface v3
Tests basic functionality of the v3 interface
"""

import requests
import json
import sys
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_TIMEOUT = 10

def test_basic_connectivity():
    """Test basic connectivity to the v3 interface"""
    print("🔍 Testing basic connectivity...")

    try:
        response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print("✅ Root route accessible")
            return True
        else:
            print(f"❌ Root route returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to server: {e}")
        return False

def test_v3_route():
    """Test v3 route"""
    print("🔍 Testing v3 route...")

    try:
        response = requests.get(f"{BASE_URL}/v3", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print("✅ v3 route accessible")
            return True
        else:
            print(f"❌ v3 route returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to v3 route: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    print("🔍 Testing API endpoints...")

    endpoints = [
        "/api/v3/config/main",
        "/api/v3/system/status",
        "/api/v3/plugins/installed",
        "/api/v3/fonts/catalog"
    ]

    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                print(f"✅ {endpoint} accessible")
                results.append(True)
            else:
                print(f"❌ {endpoint} returned status {response.status_code}")
                results.append(False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to {endpoint}: {e}")
            results.append(False)

    return all(results)

def test_sse_streams():
    """Test SSE streams"""
    print("🔍 Testing SSE streams...")

    streams = [
        "/api/v3/stream/stats",
        "/api/v3/stream/display",
        "/api/v3/stream/logs"
    ]

    results = []
    for stream in streams:
        try:
            response = requests.get(f"{BASE_URL}{stream}", timeout=TEST_TIMEOUT, stream=True)
            if response.status_code == 200 and 'text/event-stream' in response.headers.get('Content-Type', ''):
                print(f"✅ {stream} accessible")
                results.append(True)
            else:
                print(f"❌ {stream} returned status {response.status_code}")
                results.append(False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to {stream}: {e}")
            results.append(False)

    return all(results)

def test_htmx_partials():
    """Test HTMX partial loading"""
    print("🔍 Testing HTMX partials...")

    partials = [
        "/v3/partials/overview",
        "/v3/partials/general",
        "/v3/partials/display",
        "/v3/partials/sports",
        "/v3/partials/plugins",
        "/v3/partials/fonts",
        "/v3/partials/logs"
    ]

    results = []
    for partial in partials:
        try:
            response = requests.get(f"{BASE_URL}{partial}", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                print(f"✅ {partial} accessible")
                results.append(True)
            else:
                print(f"❌ {partial} returned status {response.status_code}")
                results.append(False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to {partial}: {e}")
            results.append(False)

    return all(results)

def test_form_submissions():
    """Test basic form submissions"""
    print("🔍 Testing form submissions...")

    # Test system action
    try:
        response = requests.post(
            f"{BASE_URL}/api/v3/system/action",
            json={"action": "git_pull"},
            timeout=TEST_TIMEOUT
        )
        if response.status_code in [200, 400]:  # 400 is expected for invalid actions
            print("✅ System action endpoint accessible")
            return True
        else:
            print(f"❌ System action returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test system action: {e}")
        return False

def test_configuration_save():
    """Test configuration saving"""
    print("🔍 Testing configuration save...")

    # Test main config save
    try:
        test_config = {
            "web_display_autostart": True,
            "timezone": "America/Chicago"
        }

        response = requests.post(
            f"{BASE_URL}/api/v3/config/main",
            json=test_config,
            timeout=TEST_TIMEOUT
        )

        if response.status_code == 200:
            print("✅ Configuration save accessible")
            return True
        else:
            print(f"❌ Configuration save returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test configuration save: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting LED Matrix Web Interface v3 Tests")
    print("=" * 50)

    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("v3 Route", test_v3_route),
        ("API Endpoints", test_api_endpoints),
        ("SSE Streams", test_sse_streams),
        ("HTMX Partials", test_htmx_partials),
        ("Form Submissions", test_form_submissions),
        ("Configuration Save", test_configuration_save)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! v3 interface is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
