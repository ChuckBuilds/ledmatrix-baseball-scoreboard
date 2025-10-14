#!/usr/bin/env python3
"""
Test script to verify plugin manager API endpoints are working correctly.
Run this on the Raspberry Pi to test the web interface API.
"""

import requests
import json
import sys

def test_endpoint(url, endpoint_name):
    """Test a single API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Status: {data.get('status', 'N/A')}")
                
                if 'data' in data:
                    if 'plugins' in data['data']:
                        print(f"Plugins Count: {len(data['data']['plugins'])}")
                        if data['data']['plugins']:
                            print("\nFirst 3 plugins:")
                            for plugin in data['data']['plugins'][:3]:
                                print(f"  - {plugin.get('id')}: {plugin.get('name')}")
                    else:
                        print(f"Data keys: {list(data['data'].keys())}")
                
                if 'message' in data:
                    print(f"Message: {data['message']}")
                    
                print(f"\n✅ SUCCESS")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ ERROR: Failed to parse JSON: {e}")
                print(f"Response text: {response.text[:200]}")
                return False
        else:
            print(f"❌ ERROR: Non-200 status code")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ ERROR: Request failed: {e}")
        return False

def main():
    """Main test function"""
    # Default to localhost, but can be changed
    base_url = "http://localhost:5000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"\n{'#'*60}")
    print(f"# Plugin Manager API Test")
    print(f"# Base URL: {base_url}")
    print(f"{'#'*60}")
    
    results = {}
    
    # Test installed plugins endpoint
    results['installed'] = test_endpoint(
        f"{base_url}/api/v3/plugins/installed",
        "Installed Plugins"
    )
    
    # Test plugin store endpoint
    results['store'] = test_endpoint(
        f"{base_url}/api/v3/plugins/store/list",
        "Plugin Store"
    )
    
    # Test GitHub auth status
    results['github'] = test_endpoint(
        f"{base_url}/api/v3/plugins/store/github-status",
        "GitHub Auth Status"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name.upper()}: {status}")
    
    all_passed = all(results.values())
    print(f"\n{'='*60}")
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nThe API is working correctly!")
        print("If the web interface still doesn't show plugins, check:")
        print("  1. Browser console for JavaScript errors")
        print("  2. Network tab to see if requests are being made")
        print("  3. Make sure you've restarted the web service")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nThe API has issues. Check:")
        print("  1. Is the web service running?")
        print("  2. Check web service logs: sudo journalctl -u ledmatrix-web -n 50")
        print("  3. Verify plugin managers are initialized in app.py")
    
    print(f"{'='*60}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

