#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capture screenshots of Luzmo dashboards using Playwright.
"""

import sys
import io
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_screenshot import DashboardScreenshot


def main():
    parser = argparse.ArgumentParser(
        description='Capture screenshots of Luzmo dashboards'
    )
    parser.add_argument(
        '--dashboard', '-d',
        help='Specific dashboard ID to capture (optional)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of dashboards to capture'
    )
    parser.add_argument(
        '--output', '-o',
        default='screenshots',
        help='Output directory for screenshots (default: screenshots)'
    )
    parser.add_argument(
        '--width', '-W',
        type=int,
        default=1920,
        help='Viewport width (default: 1920)'
    )
    parser.add_argument(
        '--height', '-H',
        type=int,
        default=1080,
        help='Viewport height (default: 1080)'
    )
    parser.add_argument(
        '--wait', '-w',
        type=int,
        default=5000,
        help='Wait time in ms for dashboard to load (default: 5000)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luzmo Dashboard Screenshot Capture")
    print("=" * 80)
    print()
    print(f"Output directory: {args.output}")
    print(f"Viewport: {args.width}x{args.height}")
    print(f"Wait time: {args.wait}ms")
    if args.limit:
        print(f"Limit: {args.limit} dashboards")
    print()

    try:
        capturer = DashboardScreenshot(
            output_dir=args.output,
            width=args.width,
            height=args.height
        )

        if args.dashboard:
            # Single dashboard
            print(f"Capturing dashboard: {args.dashboard}")
            screenshot_path = capturer.capture_single(args.dashboard, wait_time=args.wait)

            if screenshot_path:
                print(f"\nScreenshot saved: {screenshot_path}")
            else:
                print("\nFailed to capture screenshot")
                sys.exit(1)
        else:
            # All dashboards
            results = capturer.capture_all(limit=args.limit, wait_time=args.wait)

            # Summary
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful

            print()
            print("=" * 80)
            print("Capture complete!")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            print(f"  Output: {args.output}/")
            print("=" * 80)

            if failed > 0:
                print("\nFailed dashboards:")
                for r in results:
                    if not r['success']:
                        print(f"  - {r['name']} ({r['id']})")

    except ImportError as e:
        print(f"Error: {str(e)}")
        print("\nTo install Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)


if __name__ == "__main__":
    main()
