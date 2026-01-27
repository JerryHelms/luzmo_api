#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export all Luzmo datasets, columns, and usage to Excel.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dataset_exporter import DatasetExporter


def main():
    print("=" * 80)
    print("Luzmo Dataset Exporter")
    print("=" * 80)
    print()

    exporter = DatasetExporter()
    output_file = exporter.export_to_excel()

    print()
    print("=" * 80)
    print("Export complete!")
    print(f"File: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
