#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capture screenshots of Luzmo dashboards using authenticated login (no embed required).
"""

import sys
import io
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_screenshot_auth import DashboardScreenshotAuth


def main():
    parser = argparse.ArgumentParser(
        description='Capture screenshots of Luzmo dashboards using login authentication'
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
    parser.add_argument(
        '--email', '-e',
        help='Luzmo login email (or set LUZMO_EMAIL env var)'
    )
    parser.add_argument(
        '--password', '-p',
        help='Luzmo login password (or set LUZMO_PASSWORD env var)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (saves screenshots and HTML for troubleshooting)'
    )
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        default=True,
        help='Enable fullscreen/preview mode before screenshot (default: True)'
    )
    parser.add_argument(
        '--no-fullscreen',
        action='store_false',
        dest='fullscreen',
        help='Disable fullscreen mode'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luzmo Dashboard Screenshot Capture (Authenticated)")
    print("=" * 80)
    print()
    print(f"Output directory: {args.output}")
    print(f"Viewport: {args.width}x{args.height}")
    print(f"Wait time: {args.wait}ms")
    if args.limit:
        print(f"Limit: {args.limit} dashboards")
    print()

    try:
        capturer = DashboardScreenshotAuth(
            output_dir=args.output,
            width=args.width,
            height=args.height,
            email=args.email,
            password=args.password,
            fullscreen=args.fullscreen,
            debug=args.debug
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

    except ValueError as e:
        print(f"Configuration Error: {str(e)}")
        print("\nTo set credentials:")
        print("  Option 1: Set environment variables")
        print("    set LUZMO_EMAIL=your-email@example.com")
        print("    set LUZMO_PASSWORD=your-password")
        print()
        print("  Option 2: Pass as command-line arguments")
        print("    python capture_screenshots_auth.py --email your-email --password your-password")
        sys.exit(1)
    except ImportError as e:
        print(f"Error: {str(e)}")
        print("\nTo install Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)


if __name__ == "__main__":
    main()
