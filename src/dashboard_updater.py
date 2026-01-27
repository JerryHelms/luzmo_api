"""
Dashboard Updater
Reads dashboard descriptions from an external file and updates Luzmo dashboards.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path

from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name, get_dashboard_description


class DashboardUpdater:
    """Updates Luzmo dashboards from external data sources."""

    def __init__(self, client: Optional[LuzmoClient] = None):
        """
        Initialize dashboard updater.

        Args:
            client: LuzmoClient instance
        """
        self.client = client or LuzmoClient()

    def read_descriptions_from_file(self, file_path: str) -> pd.DataFrame:
        """
        Read dashboard descriptions from CSV or Excel file.

        Expected columns:
            - id: Dashboard ID (required)
            - description OR generated_description: New description text

        Args:
            file_path: Path to CSV or Excel file

        Returns:
            DataFrame with id and description columns
        """
        path = Path(file_path)

        if path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Validate required columns
        if 'id' not in df.columns:
            raise ValueError("File must contain 'id' column")

        # Find description column
        desc_column = None
        for col in ['description', 'generated_description', 'new_description']:
            if col in df.columns:
                desc_column = col
                break

        if desc_column is None:
            raise ValueError("File must contain 'description', 'generated_description', or 'new_description' column")

        # Standardize column names
        df = df.rename(columns={desc_column: 'description'})

        return df[['id', 'description']].dropna(subset=['id', 'description'])

    def update_dashboard_description(
        self,
        dashboard_id: str,
        description: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Update a single dashboard's description.

        Args:
            dashboard_id: Dashboard ID
            description: New description text
            language: Language code (default: 'en')

        Returns:
            API response
        """
        # Luzmo stores descriptions as language dicts: {'en': 'text'}
        description_obj = {language: description}

        response = self.client._make_request(
            action='update',
            resource='securable',
            id=dashboard_id,
            properties={
                'description': description_obj
            }
        )

        return response

    def preview_updates(self, file_path: str) -> pd.DataFrame:
        """
        Preview what updates would be made without applying them.

        Args:
            file_path: Path to descriptions file

        Returns:
            DataFrame showing current vs new descriptions
        """
        df = self.read_descriptions_from_file(file_path)

        previews = []
        for _, row in df.iterrows():
            dashboard_id = row['id']
            new_description = row['description']

            # Get current dashboard info
            try:
                response = self.client._make_request(
                    action='get',
                    resource='securable',
                    find={
                        'where': {'id': dashboard_id},
                        'attributes': ['id', 'name', 'description']
                    }
                )
                rows = response.get('rows', [])
                if rows:
                    dashboard = rows[0]
                    current_desc = get_dashboard_description(dashboard)
                    name = get_dashboard_name(dashboard)
                else:
                    current_desc = '[Dashboard not found]'
                    name = '[Not found]'
            except Exception as e:
                current_desc = f'[Error: {str(e)}]'
                name = '[Error]'

            previews.append({
                'id': dashboard_id,
                'name': name,
                'current_description': current_desc[:100] + '...' if len(current_desc) > 100 else current_desc,
                'new_description': new_description[:100] + '...' if len(str(new_description)) > 100 else new_description
            })

        return pd.DataFrame(previews)

    def update_from_file(
        self,
        file_path: str,
        dry_run: bool = False,
        language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """
        Update multiple dashboards from a file.

        Args:
            file_path: Path to descriptions file
            dry_run: If True, only preview changes without applying
            language: Language code for descriptions

        Returns:
            List of update results
        """
        df = self.read_descriptions_from_file(file_path)

        results = []
        total = len(df)

        for i, row in df.iterrows():
            dashboard_id = row['id']
            description = row['description']

            print(f"Processing {i+1}/{total}: {dashboard_id}")

            if dry_run:
                results.append({
                    'id': dashboard_id,
                    'status': 'dry_run',
                    'description': description[:50] + '...'
                })
            else:
                try:
                    response = self.update_dashboard_description(
                        dashboard_id=dashboard_id,
                        description=description,
                        language=language
                    )
                    results.append({
                        'id': dashboard_id,
                        'status': 'success',
                        'response': response
                    })
                except Exception as e:
                    results.append({
                        'id': dashboard_id,
                        'status': 'error',
                        'error': str(e)
                    })

        return results

    def update_single(
        self,
        dashboard_id: str,
        description: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Update a single dashboard's description.

        Args:
            dashboard_id: Dashboard ID
            description: New description
            language: Language code

        Returns:
            Result dict with status
        """
        try:
            response = self.update_dashboard_description(
                dashboard_id=dashboard_id,
                description=description,
                language=language
            )
            return {
                'id': dashboard_id,
                'status': 'success',
                'response': response
            }
        except Exception as e:
            return {
                'id': dashboard_id,
                'status': 'error',
                'error': str(e)
            }


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.dashboard_updater <file_path> [--dry-run]")
        print()
        print("File should have columns: id, description (or generated_description)")
        return

    file_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    updater = DashboardUpdater()

    if dry_run:
        print("DRY RUN - No changes will be made")
        print()

    print("Preview of updates:")
    preview = updater.preview_updates(file_path)
    print(preview.to_string(index=False))
    print()

    if not dry_run:
        confirm = input("Proceed with updates? (yes/no): ")
        if confirm.lower() == 'yes':
            results = updater.update_from_file(file_path)
            success = sum(1 for r in results if r['status'] == 'success')
            errors = sum(1 for r in results if r['status'] == 'error')
            print(f"\nCompleted: {success} successful, {errors} errors")
        else:
            print("Cancelled")


if __name__ == "__main__":
    main()
