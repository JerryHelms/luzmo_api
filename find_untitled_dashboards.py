#!/usr/bin/env python3
"""
Find and optionally delete untitled or empty dashboards.
"""

import argparse
import subprocess
from pathlib import Path
from src.luzmo_client import LuzmoClient
from src.utils import get_dashboard_name
from dotenv import load_dotenv

load_dotenv()

def find_untitled_dashboards():
    """Find all untitled dashboards."""
    client = LuzmoClient()

    # Get all dashboards
    response = client._make_request(
        action='get',
        resource='securable',
        find={
            'where': {
                'type': 'dashboard',
                'derived': False
            },
            'attributes': ['id', 'name', 'slug', 'subtype', 'created_at', 'modified_at'],
            'order': [['modified_at', 'desc']]
        }
    )

    dashboards = response.get('rows', [])

    # Find untitled dashboards
    untitled = []
    for dashboard in dashboards:
        name = get_dashboard_name(dashboard)

        # Check if untitled or empty
        if not name or name.strip() == '' or name.lower() == 'untitled dashboard' or name.lower() == 'untitled':
            untitled.append({
                'id': dashboard.get('id'),
                'name': name or '(empty)',
                'subtype': dashboard.get('subtype'),
                'created_at': dashboard.get('created_at'),
                'modified_at': dashboard.get('modified_at')
            })

    return untitled

def delete_dashboard(dashboard_id: str):
    """Delete a dashboard by ID."""
    client = LuzmoClient()

    try:
        response = client._make_request(
            action='delete',
            resource='securable',
            id=dashboard_id
        )
        return True
    except Exception as e:
        print(f"Error deleting dashboard {dashboard_id}: {str(e)}")
        return False

def delete_related_files(dashboard_id: str):
    """Delete screenshot and documentation files for a dashboard."""
    deleted_files = []

    # Get short ID (first 8 chars)
    short_id = dashboard_id.split('-')[0] if '-' in dashboard_id else dashboard_id[:8]

    # Delete screenshots with this ID
    screenshots_dir = Path('screenshots')
    if screenshots_dir.exists():
        for screenshot in screenshots_dir.glob(f'*_{short_id}.png'):
            try:
                screenshot.unlink()
                deleted_files.append(str(screenshot))
            except Exception as e:
                print(f"    Warning: Could not delete {screenshot}: {e}")

    # Delete documentation files
    docs_dir = Path('dashboard_docs')
    if docs_dir.exists():
        doc_file = docs_dir / f'dashboard_{short_id}.md'
        if doc_file.exists():
            try:
                doc_file.unlink()
                deleted_files.append(str(doc_file))
            except Exception as e:
                print(f"    Warning: Could not delete {doc_file}: {e}")

    return deleted_files

def regenerate_readme():
    """Regenerate the dashboard_docs README.md."""
    try:
        result = subprocess.run(
            ['python', 'generate_dashboard_index.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return True
        else:
            print(f"    Warning: Failed to regenerate README: {result.stderr}")
            return False
    except Exception as e:
        print(f"    Warning: Could not regenerate README: {e}")
        return False

def main():
    """Find and optionally delete untitled dashboards."""
    parser = argparse.ArgumentParser(description='Find and delete untitled dashboards')
    parser.add_argument('--delete', action='store_true', help='Automatically delete without prompting')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    args = parser.parse_args()

    print("Finding untitled dashboards...")
    print("=" * 80)

    untitled = find_untitled_dashboards()

    if not untitled:
        print("\n[OK] No untitled dashboards found!")
        return

    print(f"\nFound {len(untitled)} untitled dashboard(s):\n")

    for i, dashboard in enumerate(untitled, 1):
        print(f"{i}. ID: {dashboard['id']}")
        print(f"   Name: {dashboard['name']}")
        print(f"   Type: {dashboard['subtype']}")
        print(f"   Created: {dashboard['created_at']}")
        print(f"   Modified: {dashboard['modified_at']}")
        print()

    # Determine if we should delete
    should_delete = args.delete

    if args.dry_run:
        print("\n[DRY RUN] Would delete these dashboards (use --delete to actually delete)")
        return

    if not should_delete:
        # Ask user if they want to delete
        print("=" * 80)
        try:
            response = input(f"\nDo you want to delete these {len(untitled)} untitled dashboard(s)? (yes/no): ")
            should_delete = response.lower() in ['yes', 'y']
        except (EOFError, KeyboardInterrupt):
            print("\n\nCancelled. Use --delete flag to delete without prompting.")
            return

    if should_delete:
        print(f"\nDeleting {len(untitled)} dashboards and related files...")

        deleted_dashboards = 0
        failed_dashboards = 0
        deleted_files = []

        for dashboard in untitled:
            dashboard_id = dashboard['id']
            print(f"\nDeleting dashboard {dashboard_id} ({dashboard['name']})...")

            # Delete the dashboard from Luzmo
            if delete_dashboard(dashboard_id):
                print("  [OK] Dashboard deleted from Luzmo")
                deleted_dashboards += 1

                # Delete related files
                print("  Cleaning up related files...")
                files = delete_related_files(dashboard_id)
                if files:
                    for file in files:
                        print(f"    - Deleted: {file}")
                    deleted_files.extend(files)
                else:
                    print("    - No related files found")
            else:
                print("  [ERROR] Failed to delete dashboard")
                failed_dashboards += 1

        # Regenerate README
        if deleted_dashboards > 0:
            print(f"\nRegenerating dashboard_docs/README.md...")
            if regenerate_readme():
                print("  [OK] README.md updated")
            else:
                print("  [WARNING] README.md may need manual update")

        print(f"\n" + "=" * 80)
        print(f"\nSummary:")
        print(f"  Dashboards deleted: {deleted_dashboards}")
        print(f"  Dashboards failed: {failed_dashboards}")
        print(f"  Files deleted: {len(deleted_files)}")
        if deleted_files:
            print(f"\nDeleted files:")
            for file in deleted_files:
                print(f"  - {file}")
    else:
        print("\nCancelled. No dashboards were deleted.")

if __name__ == '__main__':
    main()
