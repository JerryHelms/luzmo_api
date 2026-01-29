"""
Dashboard Screenshot Capture
Uses Playwright to capture screenshots of Luzmo dashboards.

Requires embed access to be configured in your Luzmo account.
See: https://developer.luzmo.com/docs/embedding
"""

import os
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name

# Playwright imports (optional)
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Official Luzmo SDK (optional, for authorization)
try:
    from luzmo.luzmo import Luzmo
    LUZMO_SDK_AVAILABLE = True
except ImportError:
    LUZMO_SDK_AVAILABLE = False


class DashboardScreenshot:
    """Captures screenshots of Luzmo dashboards using Playwright."""

    def __init__(
        self,
        client: Optional[LuzmoClient] = None,
        output_dir: str = "screenshots",
        width: int = 1920,
        height: int = 1080,
        embed_key: Optional[str] = None,
        embed_token: Optional[str] = None
    ):
        """
        Initialize screenshot capturer.

        Args:
            client: LuzmoClient instance
            output_dir: Directory to save screenshots
            width: Viewport width
            height: Viewport height
            embed_key: Optional pre-generated embed key
            embed_token: Optional pre-generated embed token
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )

        self.client = client or LuzmoClient()
        self.output_dir = Path(output_dir)
        self.width = width
        self.height = height
        self.embed_key = embed_key or os.getenv('LUZMO_EMBED_KEY')
        self.embed_token = embed_token or os.getenv('LUZMO_EMBED_TOKEN')

        # Initialize official Luzmo SDK if available
        self.luzmo_client = None
        if LUZMO_SDK_AVAILABLE:
            key = os.getenv('LUZMO_API_KEY')
            token = os.getenv('LUZMO_API_TOKEN')
            host = os.getenv('LUZMO_API_HOST', 'https://api.us.luzmo.com')
            if key and token:
                self.luzmo_client = Luzmo(key, token, host)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """
        Fetch all dashboards with slug information.

        Returns:
            List of dashboard objects
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard',
                    'derived': False
                },
                'attributes': ['id', 'name', 'slug', 'subtype'],
                'order': [['modified_at', 'desc']]
            }
        )
        return response.get('rows', [])

    def create_embed_authorization(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Create an authorization token for embedding a dashboard.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Authorization response with key/token or None if failed
        """
        if not self.luzmo_client:
            return None

        try:
            expiry = int(time.time()) + 3600  # 1 hour from now
            auth = self.luzmo_client.create('authorization', {
                'type': 'embed',
                'expiry': expiry,
                'securables': [dashboard_id]
            })
            return auth
        except Exception as e:
            print(f"  Warning: Could not create embed authorization: {e}")
            return None

    def get_app_host(self) -> str:
        """Get the Luzmo app host based on API host."""
        host = os.getenv('LUZMO_API_HOST', 'https://api.us.luzmo.com')

        if 'api.us.luzmo.com' in host:
            return 'https://app.us.luzmo.com'
        elif 'api.eu.luzmo.com' in host:
            return 'https://app.eu.luzmo.com'
        else:
            return 'https://app.luzmo.com'

    def get_embed_url(self, dashboard_id: str) -> Optional[str]:
        """
        Get the embed URL for a dashboard.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Full embed URL with authentication or None if not available
        """
        app_host = self.get_app_host()

        # Option 1: Use pre-configured embed credentials
        if self.embed_key and self.embed_token:
            return f"{app_host}/embed/{dashboard_id}?key={self.embed_key}&token={self.embed_token}"

        # Option 2: Create dynamic authorization
        auth = self.create_embed_authorization(dashboard_id)
        if auth and auth.get('id') and auth.get('token'):
            return f"{app_host}/embed/{dashboard_id}?key={auth['id']}&token={auth['token']}"

        return None

    def get_public_url(self, dashboard_id: str, slug: str = None) -> str:
        """
        Get a public/direct URL for a dashboard (requires public sharing enabled).

        Args:
            dashboard_id: Dashboard ID
            slug: Optional dashboard slug

        Returns:
            Public dashboard URL
        """
        app_host = self.get_app_host()
        if slug:
            return f"{app_host}/s/{slug}"
        return f"{app_host}/d/{dashboard_id}"

    async def capture_screenshot_async(
        self,
        browser: Browser,
        dashboard_id: str,
        dashboard_name: str,
        slug: str = None,
        wait_time: int = 5000
    ) -> Optional[str]:
        """
        Capture a screenshot of a single dashboard.

        Args:
            browser: Playwright browser instance
            dashboard_id: Dashboard ID
            dashboard_name: Dashboard name for filename
            slug: Optional dashboard slug for public URL
            wait_time: Time to wait for dashboard to load (ms)

        Returns:
            Path to saved screenshot or None if failed
        """
        page = None
        try:
            # Try to get embed URL first
            url = self.get_embed_url(dashboard_id)

            if not url:
                # Fall back to public URL (requires public sharing enabled in Luzmo)
                url = self.get_public_url(dashboard_id, slug)
                print(f"  Using public URL (embed auth not available)")

            # Create new page
            page = await browser.new_page()
            await page.set_viewport_size({"width": self.width, "height": self.height})

            # Navigate to dashboard
            await page.goto(url, wait_until='networkidle', timeout=60000)

            # Wait for dashboard to render
            await page.wait_for_timeout(wait_time)

            # Check if we got an error page
            content = await page.content()
            if 'error' in content.lower() and 'access' in content.lower():
                print(f"  Access denied - dashboard may require authentication")
                return None

            # Generate safe filename
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in dashboard_name)
            safe_name = safe_name[:50]  # Limit length
            filename = f"{safe_name}_{dashboard_id[:8]}.png"
            filepath = self.output_dir / filename

            # Capture screenshot
            await page.screenshot(path=str(filepath), full_page=True)

            return str(filepath)

        except Exception as e:
            print(f"  Error capturing {dashboard_name}: {str(e)}")
            return None
        finally:
            if page:
                await page.close()

    async def capture_all_async(
        self,
        limit: Optional[int] = None,
        wait_time: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        Capture screenshots of all dashboards.

        Args:
            limit: Optional limit on number of dashboards
            wait_time: Time to wait for each dashboard to load (ms)

        Returns:
            List of results with dashboard info and screenshot paths
        """
        # Fetch dashboards
        print("Fetching dashboards...")
        dashboards = self.get_all_dashboards()
        print(f"Found {len(dashboards)} dashboards")

        if limit:
            dashboards = dashboards[:limit]

        results = []

        async with async_playwright() as p:
            # Launch browser
            print("Launching browser...")
            browser = await p.chromium.launch(headless=True)

            try:
                for i, dash in enumerate(dashboards, 1):
                    dashboard_id = dash.get('id', '')
                    dashboard_name = get_dashboard_name(dash)
                    slug = dash.get('slug', '')

                    print(f"Capturing {i}/{len(dashboards)}: {dashboard_name}")

                    screenshot_path = await self.capture_screenshot_async(
                        browser,
                        dashboard_id,
                        dashboard_name,
                        slug=slug,
                        wait_time=wait_time
                    )

                    results.append({
                        'id': dashboard_id,
                        'name': dashboard_name,
                        'screenshot_path': screenshot_path,
                        'success': screenshot_path is not None
                    })

            finally:
                await browser.close()

        # Summary
        successful = sum(1 for r in results if r['success'])
        print(f"\nCapture complete: {successful}/{len(results)} successful")
        print(f"Screenshots saved to: {self.output_dir.absolute()}")

        return results

    def capture_all(
        self,
        limit: Optional[int] = None,
        wait_time: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for capture_all_async.

        Args:
            limit: Optional limit on number of dashboards
            wait_time: Time to wait for each dashboard to load (ms)

        Returns:
            List of results with dashboard info and screenshot paths
        """
        return asyncio.run(self.capture_all_async(limit=limit, wait_time=wait_time))

    def capture_single(
        self,
        dashboard_id: str,
        wait_time: int = 5000
    ) -> Optional[str]:
        """
        Capture screenshot of a single dashboard.

        Args:
            dashboard_id: Dashboard ID
            wait_time: Time to wait for dashboard to load (ms)

        Returns:
            Path to saved screenshot or None if failed
        """
        async def _capture():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    # Get dashboard name
                    response = self.client._make_request(
                        action='get',
                        resource='securable',
                        find={
                            'where': {'id': dashboard_id},
                            'attributes': ['id', 'name']
                        }
                    )
                    rows = response.get('rows', [])
                    if not rows:
                        print(f"Dashboard {dashboard_id} not found")
                        return None

                    dashboard_name = get_dashboard_name(rows[0])
                    return await self.capture_screenshot_async(
                        browser,
                        dashboard_id,
                        dashboard_name,
                        wait_time
                    )
                finally:
                    await browser.close()

        return asyncio.run(_capture())


def main():
    """Main function to capture dashboard screenshots."""
    capturer = DashboardScreenshot()
    results = capturer.capture_all(limit=5)  # Test with 5 dashboards

    print("\nResults:")
    for r in results:
        status = "OK" if r['success'] else "FAILED"
        print(f"  [{status}] {r['name']}")


if __name__ == "__main__":
    main()
