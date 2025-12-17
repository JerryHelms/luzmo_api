"""
Utility functions for working with Luzmo API data.
"""

from typing import Dict, Any, Union, List
from datetime import datetime


def get_dashboard_name(dashboard: Dict[str, Any], preferred_lang: str = 'en') -> str:
    """
    Extract dashboard name from Luzmo dashboard object.

    Dashboard names in Luzmo are stored as language dictionaries like:
    {'en': 'Dashboard Name', 'nl': 'Dashboard Naam'}

    Args:
        dashboard: Dashboard object from Luzmo API
        preferred_lang: Preferred language code (default: 'en')

    Returns:
        Dashboard name as string
    """
    name = dashboard.get('name', {})

    if isinstance(name, str):
        return name
    elif isinstance(name, dict):
        # Try preferred language first
        if preferred_lang in name:
            return name[preferred_lang]

        # Fallback to first available language
        if name:
            return list(name.values())[0]

        return 'Unnamed Dashboard'
    else:
        return 'Unnamed Dashboard'


def get_dashboard_description(dashboard: Dict[str, Any], preferred_lang: str = 'en') -> str:
    """
    Extract dashboard description from Luzmo dashboard object.

    Args:
        dashboard: Dashboard object from Luzmo API
        preferred_lang: Preferred language code (default: 'en')

    Returns:
        Dashboard description as string
    """
    description = dashboard.get('description', {})

    if isinstance(description, str):
        return description
    elif isinstance(description, dict):
        # Try preferred language first
        if preferred_lang in description:
            return description[preferred_lang]

        # Fallback to first available language
        if description:
            return list(description.values())[0]

        return ''
    else:
        return ''


def filter_recent_dashboards(dashboards: List[Dict[str, Any]], years_back: int = 2) -> List[Dict[str, Any]]:
    """
    Filter dashboards to show only recently created ones (likely user-created, not templates).

    Args:
        dashboards: List of dashboard objects
        years_back: How many years back to consider (default: 2)

    Returns:
        Filtered list of dashboards
    """
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=365 * years_back)

    recent_dashboards = []
    for dashboard in dashboards:
        created_at = dashboard.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if created_date > cutoff_date:
                    recent_dashboards.append(dashboard)
            except:
                # If date parsing fails, include it to be safe
                recent_dashboards.append(dashboard)
        else:
            # If no created_at, include it to be safe
            recent_dashboards.append(dashboard)

    return recent_dashboards


def filter_dashboards_by_name_pattern(dashboards: List[Dict[str, Any]], exclude_patterns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Filter out dashboards that match certain name patterns (e.g., templates).

    Args:
        dashboards: List of dashboard objects
        exclude_patterns: List of strings to exclude if found in dashboard name

    Returns:
        Filtered list of dashboards
    """
    if exclude_patterns is None:
        # Common template/demo patterns
        exclude_patterns = [
            'template',
            'demo',
            'sample',
            'example',
            'cumul.io',
            'luzmo',
            'euro2016',
            'spotify'
        ]

    filtered = []
    for dashboard in dashboards:
        name = get_dashboard_name(dashboard).lower()

        # Check if any exclude pattern is in the name
        if not any(pattern.lower() in name for pattern in exclude_patterns):
            filtered.append(dashboard)

    return filtered
