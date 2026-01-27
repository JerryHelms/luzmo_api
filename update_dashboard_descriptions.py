#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Luzmo dashboard descriptions from an external file.
"""

import sys
import io
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_updater import DashboardUpdater


def main():
    parser = argparse.ArgumentParser(
        description='Update Luzmo dashboard descriptions from file'
    )
    parser.add_argument(
        'file',
        help='CSV or Excel file with id and description columns'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    parser.add_argument(
        '--language', '-l',
        default='en',
        help='Language code for descriptions (default: en)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luzmo Dashboard Description Updater")
    print("=" * 80)
    print()
    print(f"File: {args.file}")
    print(f"Language: {args.language}")
    if args.dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    print()

    updater = DashboardUpdater()

    # Show preview
    print("Preview of updates:")
    print("-" * 80)
    preview = updater.preview_updates(args.file)
    print(preview.to_string(index=False))
    print("-" * 80)
    print()

    if args.dry_run:
        print("Dry run complete. No changes were made.")
        return

    # Confirm
    if not args.no_confirm:
        confirm = input(f"Update {len(preview)} dashboards? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return

    # Execute updates
    print()
    print("Updating dashboards...")
    results = updater.update_from_file(args.file, language=args.language)

    # Summary
    success = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')

    print()
    print("=" * 80)
    print(f"Complete: {success} successful, {errors} errors")

    if errors > 0:
        print()
        print("Errors:")
        for r in results:
            if r['status'] == 'error':
                print(f"  {r['id']}: {r['error']}")

    print("=" * 80)


if __name__ == "__main__":
    main()
