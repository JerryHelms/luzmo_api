#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export all Luzmo dashboards and their details to Excel.
Does not retrieve actual data or submit to LLM.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_exporter import DashboardExporter


def main():
    print("=" * 80)
    print("Luzmo Dashboard Exporter")
    print("=" * 80)
    print()

    exporter = DashboardExporter()
    output_file = exporter.export_to_excel()

    print()
    print("=" * 80)
    print(f"Export complete!")
    print(f"File: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
