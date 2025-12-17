#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive script to list dashboards and optionally analyze them with Claude.
"""

from src.luzmo_client import LuzmoClient
from src.dashboard_summary_pipeline import DashboardSummaryPipeline
from src.utils import get_dashboard_name, get_dashboard_description
import sys
import io

# Fix Windows console encoding for unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def list_dashboards():
    """List all available dashboards."""
    print("="*80)
    print("Luzmo Dashboard Iterator")
    print("="*80)

    try:
        client = LuzmoClient()
        print("\n✓ Connected to Luzmo API")

        print("\nFetching dashboards...")
        dashboards = client.list_dashboards()

        if len(dashboards) == 0:
            print("\n⚠ No dashboards found in your Luzmo account")
            print("\nTo use this tool:")
            print("1. Log in to your Luzmo account")
            print("2. Create one or more dashboards")
            print("3. Run this script again")
            return []

        print(f"\n✓ Found {len(dashboards)} dashboard(s):\n")
        print("-"*80)

        for i, dashboard in enumerate(dashboards, 1):
            name = get_dashboard_name(dashboard)
            dash_id = dashboard.get('id', 'N/A')
            description = get_dashboard_description(dashboard)
            modified = dashboard.get('modified_at', 'N/A')

            print(f"\n{i}. {name}")
            print(f"   ID: {dash_id}")
            if description:
                print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            print(f"   Last Modified: {modified}")

        print("\n" + "-"*80)
        return dashboards

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


def analyze_dashboard_interactive(dashboards):
    """Interactively select and analyze a dashboard."""
    if not dashboards:
        return

    print("\n" + "="*80)
    print("Dashboard Analysis")
    print("="*80)

    try:
        # Prompt for selection
        selection = input(f"\nSelect a dashboard to analyze (1-{len(dashboards)}, or 'q' to quit): ").strip()

        if selection.lower() == 'q':
            print("Exiting...")
            return

        try:
            idx = int(selection) - 1
            if idx < 0 or idx >= len(dashboards):
                print(f"Invalid selection. Please choose 1-{len(dashboards)}")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        selected_dashboard = dashboards[idx]
        dashboard_id = selected_dashboard.get('id')
        dashboard_name = get_dashboard_name(selected_dashboard)

        print(f"\n✓ Selected: {dashboard_name} (ID: {dashboard_id})")

        # Ask for output format
        print("\nSelect output format:")
        print("1. Markdown (recommended)")
        print("2. Plain text")
        print("3. JSON (with full data)")

        format_choice = input("Choice (1-3, default: 1): ").strip() or "1"

        format_map = {
            "1": "markdown",
            "2": "text",
            "3": "json"
        }

        save_format = format_map.get(format_choice, "markdown")

        # Initialize pipeline and generate summary
        print(f"\n{'='*80}")
        print("Generating AI-powered summary with Claude...")
        print(f"{'='*80}\n")

        pipeline = DashboardSummaryPipeline(output_dir="./summaries")

        result = pipeline.generate_summary(
            dashboard_id=dashboard_id,
            save_format=save_format,
            include_raw_data=(save_format == "json")
        )

        print(f"\n{'='*80}")
        print("✓ Summary Generated Successfully!")
        print(f"{'='*80}")
        print(f"Dashboard: {result['dashboard_name']}")
        print(f"Charts Analyzed: {result['charts_analyzed']}")
        print(f"Summary saved to: {result['filepath']}")

        # Show preview
        if save_format != "json":
            print(f"\n{'='*80}")
            print("Summary Preview (first 500 characters):")
            print(f"{'='*80}\n")
            print(result['summary'][:500] + "..." if len(result['summary']) > 500 else result['summary'])

        print(f"\n{'='*80}")
        print("Done! Check the summaries/ folder for the complete analysis.")
        print(f"{'='*80}")

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during analysis: {str(e)}")
        sys.exit(1)


def main():
    """Main function."""
    print("\n")

    # List all dashboards
    dashboards = list_dashboards()

    if not dashboards:
        sys.exit(0)

    # Ask if user wants to analyze
    print("\n" + "="*80)
    analyze = input("Would you like to analyze a dashboard with AI? (y/n, default: n): ").strip().lower()

    if analyze == 'y':
        analyze_dashboard_interactive(dashboards)
    else:
        print("\n✓ Dashboard listing complete!")
        print("\nTo analyze a dashboard, run this script again and choose 'y'")
        print("Or use the DashboardSummaryPipeline class directly in your code.")


if __name__ == "__main__":
    main()
