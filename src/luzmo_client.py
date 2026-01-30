"""
Luzmo API Client
Handles authentication and API requests to Luzmo.
"""

import requests
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class LuzmoClient:
    """Client for interacting with Luzmo API."""

    def __init__(self, api_key: Optional[str] = None, api_token: Optional[str] = None, host: Optional[str] = None):
        """
        Initialize Luzmo API client.

        Args:
            api_key: Luzmo API key (defaults to LUZMO_API_KEY env var)
            api_token: Luzmo API token (defaults to LUZMO_API_TOKEN env var)
            host: Luzmo API host (defaults to LUZMO_API_HOST env var)
        """
        self.api_key = api_key or os.getenv('LUZMO_API_KEY')
        self.api_token = api_token or os.getenv('LUZMO_API_TOKEN')
        self.host = host or os.getenv('LUZMO_API_HOST', 'https://api.luzmo.com')
        self.api_version = '0.1.0'

        if not self.api_key or not self.api_token:
            raise ValueError("API key and token are required. Set LUZMO_API_KEY and LUZMO_API_TOKEN environment variables.")

    def _make_request(self, action: str, resource: str, find: Optional[Dict] = None, properties: Optional[Dict] = None, id: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an API request to Luzmo using the correct payload-based authentication.

        Args:
            action: API action (get, create, update, delete)
            resource: Resource type (securable, dataset, etc.)
            find: Query parameters for get operations
            properties: Properties for create/update operations
            id: Resource ID for specific operations

        Returns:
            API response as dictionary
        """
        url = f"{self.host}/{self.api_version}/{resource}"

        # Build payload with credentials embedded (Luzmo API requirement)
        payload = {
            'action': action,
            'version': self.api_version,
            'key': self.api_key,
            'token': self.api_token
        }

        # Add query parameters for get operations
        if find is not None:
            payload['find'] = find

        # Add properties for create/update operations
        if properties is not None:
            payload['properties'] = properties

        # Add ID for specific resource operations
        if id is not None:
            payload['id'] = id

        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Handle empty responses (common for DELETE operations)
            if not response.content or response.content.strip() == b'':
                return {}

            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get dashboard metadata.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard metadata including charts, filters, etc.
        """
        response = self._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'id': dashboard_id
                }
            }
        )

        # Extract the dashboard from the response
        if isinstance(response, dict) and 'rows' in response:
            rows = response['rows']
            if rows and len(rows) > 0:
                return rows[0]
            else:
                raise Exception(f"Dashboard {dashboard_id} not found")
        elif isinstance(response, list) and len(response) > 0:
            return response[0]
        else:
            return response

    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get dashboard data (all charts).

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard data
        """
        # Note: This method may need adjustment based on actual Luzmo API data retrieval
        return self._make_request(
            action='get',
            resource='securable',
            id=dashboard_id
        )

    def get_chart(self, chart_id: str) -> Dict[str, Any]:
        """
        Get chart metadata.

        Args:
            chart_id: Chart ID

        Returns:
            Chart metadata
        """
        response = self._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'id': chart_id
                }
            }
        )

        # Extract the chart from the response
        if isinstance(response, dict) and 'rows' in response:
            rows = response['rows']
            if rows and len(rows) > 0:
                return rows[0]
            else:
                raise Exception(f"Chart {chart_id} not found")
        elif isinstance(response, list) and len(response) > 0:
            return response[0]
        else:
            return response

    def get_chart_data(self, chart_id: str) -> Dict[str, Any]:
        """
        Get data for a specific chart.

        Args:
            chart_id: Chart ID

        Returns:
            Chart data
        """
        # Note: This method may need adjustment based on actual Luzmo API data retrieval
        return self._make_request(
            action='get',
            resource='securable',
            id=chart_id
        )

    def list_dashboards(self) -> List[Dict[str, Any]]:
        """
        List all accessible dashboards.

        Returns:
            List of dashboards
        """
        response = self._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard',
                    'derived': False
                },
                'attributes': ['id', 'name', 'description', 'modified_at'],
                'order': [['modified_at', 'desc']]
            }
        )

        # Luzmo API returns {"count": N, "rows": [...]}
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and 'rows' in response:
            return response['rows']
        else:
            return response.get('data', [])
