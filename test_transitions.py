#!/usr/bin/env python3
"""
LEDMatrix Transition Test Suite

This script provides a unified interface to run all transition tests.
It includes basic functionality tests, performance tests, and decoupled frame rate tests.
"""

import sys
import os
import argparse
import time
from typing import List, Dict, Any


class TransitionTestRunner:
    """Unified test runner for LEDMatrix transition system."""

    def __init__(self):
        """Initialize the test runner."""
        self.test_results = []
        self.available_tests = {
            "basic": {
                "script": "test_transitions_basic.py",
                "description": "Basic transition functionality test",
                "category": "functionality",
            },
            "performance": {
                "script": "test_transitions_performance.py",
                "description": "High-performance transition system test",
                "category": "performance",
            },
            "decoupled": {
                "script": "test_transitions_decoupled.py",
                "description": "Decoupled frame rate and scroll speed test",
                "category": "advanced",
            },
        }

    def list_available_tests(self):
        """List all available tests."""
        print("Available Transition Tests:")
        print("=" * 40)

        for test_id, test_info in self.available_tests.items():
            status = "OK" if os.path.exists(test_info["script"]) else "MISSING"
            print(f"{status:8} {test_id:12} - {test_info['description']}")
            print(f"    Category: {test_info['category']}")
            print(f"    Script:   {test_info['script']}")
            print()

    def run_test(self, test_id: str) -> Dict[str, Any]:
        """Run a specific test."""
        if test_id not in self.available_tests:
            return {
                "success": False,
                "error": f"Unknown test: {test_id}",
                "test_id": test_id,
            }

        test_info = self.available_tests[test_id]
        script_path = test_info["script"]

        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Test script not found: {script_path}",
                "test_id": test_id,
            }

        print(f"\n{'='*60}")
        print(f"Running {test_id.upper()} Test")
        print(f"Description: {test_info['description']}")
        print(f"Script: {script_path}")
        print(f"{'='*60}")

        start_time = time.time()

        try:
            # Import and run the test
            import importlib.util

            spec = importlib.util.spec_from_file_location("test_module", script_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)

            # Run the main function if it exists
            if hasattr(test_module, "main"):
                test_module.main()

            end_time = time.time()
            duration = end_time - start_time

            return {
                "success": True,
                "test_id": test_id,
                "duration": duration,
                "description": test_info["description"],
            }

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            return {
                "success": False,
                "error": str(e),
                "test_id": test_id,
                "duration": duration,
                "description": test_info["description"],
            }

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all available tests."""
        print("LEDMatrix Transition Test Suite")
        print("=" * 40)
        print("Running all available tests...")
        print()

        results = []

        for test_id in self.available_tests.keys():
            result = self.run_test(test_id)
            results.append(result)

            if result["success"]:
                print(f"\n[OK] {test_id.upper()} test completed successfully")
            else:
                print(
                    f"\n[FAIL] {test_id.upper()} test failed: {result.get('error', 'Unknown error')}"
                )

            print("-" * 60)

        return results

    def run_category_tests(self, category: str) -> List[Dict[str, Any]]:
        """Run all tests in a specific category."""
        category_tests = [
            test_id
            for test_id, test_info in self.available_tests.items()
            if test_info["category"] == category
        ]

        if not category_tests:
            print(f"No tests found for category: {category}")
            return []

        print(f"Running {category.upper()} tests...")
        print("=" * 40)

        results = []
        for test_id in category_tests:
            result = self.run_test(test_id)
            results.append(result)

        return results

    def show_summary(self, results: List[Dict[str, Any]]):
        """Show test results summary."""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)

        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        print(f"Total tests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(
            f"Success rate: {(len(successful) / len(results)) * 100:.1f}%"
            if results
            else "0%"
        )

        if successful:
            print(f"\n[OK] Successful tests:")
            for result in successful:
                duration = result.get("duration", 0)
                print(f"  - {result['test_id']}: {duration:.2f}s")

        if failed:
            print(f"\n[FAIL] Failed tests:")
            for result in failed:
                error = result.get("error", "Unknown error")
                print(f"  - {result['test_id']}: {error}")

        print("\n" + "=" * 60)

    def show_help(self):
        """Show help information."""
        print("LEDMatrix Transition Test Suite")
        print("=" * 40)
        print()
        print("Usage:")
        print("  python test_transitions.py [options]")
        print()
        print("Options:")
        print("  --test TEST_ID     Run specific test (basic, performance, decoupled)")
        print(
            "  --category CAT     Run tests by category (functionality, performance, advanced)"
        )
        print("  --all              Run all available tests")
        print("  --list             List available tests")
        print("  --help             Show this help message")
        print()
        print("Examples:")
        print("  python test_transitions.py --list")
        print("  python test_transitions.py --test basic")
        print("  python test_transitions.py --category performance")
        print("  python test_transitions.py --all")
        print()
        print("Test Categories:")
        print("  functionality  - Basic transition functionality tests")
        print("  performance    - High-performance system tests")
        print("  advanced       - Advanced features like decoupled frame rate")
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="LEDMatrix Transition Test Suite")
    parser.add_argument("--test", help="Run specific test")
    parser.add_argument("--category", help="Run tests by category")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--list", action="store_true", help="List available tests")

    args = parser.parse_args()

    runner = TransitionTestRunner()

    if args.list:
        runner.list_available_tests()
        return

    if args.test:
        result = runner.run_test(args.test)
        runner.show_summary([result])
        return

    if args.category:
        results = runner.run_category_tests(args.category)
        runner.show_summary(results)
        return

    if args.all:
        results = runner.run_all_tests()
        runner.show_summary(results)
        return

    # Default: show help
    runner.show_help()


if __name__ == "__main__":
    main()
