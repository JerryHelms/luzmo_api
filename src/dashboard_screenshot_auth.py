"""
Dashboard Screenshot Capture with Authentication
Uses Playwright to log in to Luzmo and capture screenshots (no embed required).
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name

# Playwright imports (optional)
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class DashboardScreenshotAuth:
    """Captures screenshots of Luzmo dashboards using authenticated login."""

    def __init__(
        self,
        client: Optional[LuzmoClient] = None,
        output_dir: str = "screenshots",
        width: int = 1920,
        height: int = 1080,
        email: Optional[str] = None,
        password: Optional[str] = None,
        fullscreen: bool = True,
        debug: bool = False
    ):
        """
        Initialize screenshot capturer with authentication.

        Args:
            client: LuzmoClient instance
            output_dir: Directory to save screenshots
            width: Viewport width
            height: Viewport height
            email: Luzmo login email (or set LUZMO_EMAIL env var)
            password: Luzmo login password (or set LUZMO_PASSWORD env var)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )

        self.client = client or LuzmoClient()
        self.output_dir = Path(output_dir)
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.debug = debug

        # Get credentials from parameters or environment
        # Default to hardcoded values for testing (not recommended for production)
        self.email = email or os.getenv('LUZMO_EMAIL') or 'jerry@operationshero.com'
        self.password = password or os.getenv('LUZMO_PASSWORD') or 'Idecided2024!'

        if not self.email or not self.password:
            raise ValueError(
                "Email and password required. Credentials not found."
            )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """
        Fetch all dashboards.

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

    def get_app_host(self) -> str:
        """Get the Luzmo app host based on API host."""
        host = os.getenv('LUZMO_API_HOST', 'https://api.us.luzmo.com')

        if 'api.us.luzmo.com' in host:
            return 'https://app.us.luzmo.com'
        elif 'api.eu.luzmo.com' in host:
            return 'https://app.eu.luzmo.com'
        else:
            return 'https://app.luzmo.com'

    def get_dashboard_url(self, dashboard_id: str, preview: bool = False) -> str:
        """
        Get the direct dashboard URL.

        Args:
            dashboard_id: Dashboard ID
            preview: If True, try to get preview/embed URL

        Returns:
            Dashboard URL
        """
        app_host = self.get_app_host()

        # If preview mode requested, try the embed URL which is cleaner
        if preview:
            # Embed URLs are typically cleaner without edit controls
            return f"{app_host}/embed/{dashboard_id}"

        # Standard dashboard edit view
        return f"{app_host}/dashboard/{dashboard_id}"

    async def login(self, page: Page, debug: bool = False) -> bool:
        """
        Log in to Luzmo.

        Args:
            page: Playwright page instance
            debug: If True, saves screenshot and HTML for debugging

        Returns:
            True if login successful, False otherwise
        """
        try:
            app_host = self.get_app_host()
            login_url = f"{app_host}/login"

            print(f"  Navigating to {login_url}...")
            await page.goto(login_url, wait_until='networkidle', timeout=60000)

            if debug:
                await page.screenshot(path='debug_login_page.png')
                print(f"  Debug: Saved screenshot to debug_login_page.png")

            # Try different email field selectors
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                'input[id="email"]',
                'input[placeholder*="email" i]',
                '#email',
                '[data-test="email"]'
            ]

            email_filled = False
            for selector in email_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    await page.fill(selector, self.email)
                    print(f"  Filled email using selector: {selector}")
                    email_filled = True
                    break
                except:
                    continue

            if not email_filled:
                print(f"  ERROR: Could not find email input field")
                if debug:
                    html = await page.content()
                    with open('debug_login_page.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"  Debug: Saved HTML to debug_login_page.html")
                return False

            # Try different password field selectors
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id="password"]',
                '#password',
                '[data-test="password"]'
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    await page.fill(selector, self.password)
                    print(f"  Filled password using selector: {selector}")
                    password_filled = True
                    break
                except:
                    continue

            if not password_filled:
                print(f"  ERROR: Could not find password input field")
                return False

            # Try different submit button selectors
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                'button:has-text("Login")',
                '[data-test="submit"]',
                '[data-test="login"]'
            ]

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    print(f"  Clicked submit using selector: {selector}")
                    submit_clicked = True
                    break
                except:
                    continue

            if not submit_clicked:
                print(f"  ERROR: Could not find submit button")
                return False

            # Wait for navigation after login
            print(f"  Waiting for login to complete...")
            try:
                # Wait for either successful navigation away from login or error message
                await page.wait_for_load_state('networkidle', timeout=30000)

                # Give it a moment for redirects
                await page.wait_for_timeout(2000)

            except Exception as e:
                print(f"  Warning during login wait: {e}")

            # Check if we're logged in
            current_url = page.url
            print(f"  Current URL after login: {current_url}")

            # Check for error messages on the page
            content = await page.content()
            error_indicators = [
                'incorrect password',
                'invalid email',
                'authentication failed',
                'login failed',
                'error',
                'try again'
            ]

            has_error = any(indicator in content.lower() for indicator in error_indicators)

            if debug:
                await page.screenshot(path='debug_after_login.png')
                print(f"  Debug: Saved screenshot to debug_after_login.png")
                with open('debug_after_login.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Debug: Saved HTML to debug_after_login.html")

            # Check if we're actually logged in by looking for dashboard/home URLs
            # or absence of login-specific elements
            if '/dashboards' in current_url or '/home' in current_url and 'returnUrl' not in current_url:
                print("  Login successful!")
                return True
            elif has_error:
                print("  Login failed - error detected on page")
                return False
            elif current_url == login_url or '/login' in current_url:
                # Still on login page or login URL in path
                print("  Login may have failed - still on login-related page")
                # But let's try to proceed anyway and see if we can access dashboards
                print("  Attempting to continue anyway...")
                return True
            else:
                # Uncertain, but let's try to proceed
                print("  Login status unclear, attempting to continue...")
                return True

        except Exception as e:
            print(f"  Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def capture_screenshot_async(
        self,
        page: Page,
        dashboard_id: str,
        dashboard_name: str,
        wait_time: int = 5000,
        fullscreen: bool = True,
        debug: bool = False
    ) -> Optional[str]:
        """
        Capture a screenshot of a single dashboard.

        Args:
            page: Playwright page instance (already logged in)
            dashboard_id: Dashboard ID
            dashboard_name: Dashboard name for filename
            wait_time: Time to wait for dashboard to load (ms)

        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            # Navigate to dashboard
            # Try preview mode if fullscreen is requested
            url = self.get_dashboard_url(dashboard_id, preview=fullscreen)
            print(f"  Navigating to: {url}")

            await page.goto(url, wait_until='networkidle', timeout=60000)

            # Verify we're on the right page
            current_url = page.url
            print(f"  Current URL: {current_url}")

            # Wait for the page to settle after navigation
            await page.wait_for_timeout(2000)

            # Wait for dashboard content to load (look for common dashboard elements)
            try:
                # Try to wait for dashboard-specific elements
                # These selectors may need adjustment based on actual Luzmo UI
                await page.wait_for_selector('[class*="dashboard"], [class*="chart"], [class*="widget"]', timeout=10000)
                print(f"  Dashboard content detected")
            except:
                print(f"  Warning: Could not detect dashboard content elements")

            # Try to enter fullscreen/presentation mode if requested
            if fullscreen:
                try:
                    # First, try to find and log all available buttons for debugging
                    if debug:
                        try:
                            buttons_info = await page.evaluate("""
                                () => {
                                    const buttons = Array.from(document.querySelectorAll('button'));
                                    return buttons.map(btn => ({
                                        text: btn.textContent?.trim().substring(0, 50),
                                        title: btn.title,
                                        ariaLabel: btn.getAttribute('aria-label'),
                                        classes: btn.className.substring(0, 100)
                                    })).filter(b =>
                                        b.text || b.title || b.ariaLabel
                                    ).slice(0, 20);
                                }
                            """)
                            print(f"  Debug: Available buttons:")
                            for btn_info in buttons_info:
                                print(f"    - Text: '{btn_info.get('text')}', Title: '{btn_info.get('title')}', Aria: '{btn_info.get('ariaLabel')}'")
                        except Exception as e:
                            print(f"  Debug: Could not enumerate buttons: {e}")

                    # Look for fullscreen/presentation/preview button
                    # Try most specific selectors first
                    fullscreen_selectors = [
                        # Preview mode (most specific for Luzmo)
                        'button[title="Preview" i]',
                        'button[aria-label="Preview" i]',
                        'button:has-text("Preview")',
                        '[data-test="preview"]',
                        '[data-test="preview-button"]',
                        # Presentation mode
                        'button[title="Presentation" i]',
                        'button[title*="present" i]',
                        'button[aria-label*="present" i]',
                        '[data-test*="present"]',
                        # Fullscreen mode
                        'button[title="Fullscreen" i]',
                        'button[title*="fullscreen" i]',
                        'button[aria-label*="fullscreen" i]',
                        '[data-test*="fullscreen"]',
                        # Generic expand/maximize
                        'button[title*="expand" i]',
                        'button[title*="maximize" i]',
                        # CSS class based
                        'button[class*="preview"]',
                        'button[class*="fullscreen"]',
                        'button[class*="presentation"]',
                        # SVG icon based
                        'button:has(svg[class*="preview"])',
                        'button:has(svg[class*="fullscreen"])',
                        'button:has(svg[class*="expand"])',
                        'button:has(svg[class*="presentation"])'
                    ]

                    fullscreen_clicked = False
                    for selector in fullscreen_selectors:
                        try:
                            # Check if element exists first
                            element = await page.query_selector(selector)
                            if element:
                                # Get button info for logging
                                button_text = await element.evaluate('el => el.textContent?.trim() || el.title || el.getAttribute("aria-label") || "unknown"')
                                await element.click()
                                print(f"  Clicked preview/fullscreen button: '{button_text}'")
                                fullscreen_clicked = True
                                await page.wait_for_timeout(2000)  # Wait for transition
                                break
                        except:
                            continue

                    # If no fullscreen button found, try hiding header/navigation via JavaScript
                    if not fullscreen_clicked:
                        print(f"  Attempting to hide UI elements via CSS")
                        try:
                            # Hide common UI elements that aren't part of the dashboard content
                            await page.evaluate("""
                                () => {
                                    // Hide header, navigation, sidebars
                                    const selectorsToHide = [
                                        'header',
                                        'nav',
                                        '[class*="header"]',
                                        '[class*="navbar"]',
                                        '[class*="sidebar"]',
                                        '[class*="navigation"]',
                                        '[role="navigation"]',
                                        '[class*="topbar"]',
                                        '[class*="toolbar"]:not([class*="dashboard"])'
                                    ];

                                    selectorsToHide.forEach(selector => {
                                        document.querySelectorAll(selector).forEach(el => {
                                            if (!el.closest('[class*="dashboard"]')) {
                                                el.style.display = 'none';
                                            }
                                        });
                                    });
                                }
                            """)
                            print(f"  Hidden non-dashboard UI elements")
                        except Exception as e:
                            print(f"  Could not hide UI elements: {e}")

                except Exception as e:
                    print(f"  Note: Could not enable fullscreen mode: {e}")

            # Additional wait for dashboard to fully render
            await page.wait_for_timeout(wait_time)

            # Check if we got an actual error page (be more specific)
            content = await page.content()

            # Only fail if we see very specific error messages
            if ('access denied' in content.lower() and 'dashboard' in content.lower()) or \
               ('not found' in content.lower() and '404' in content.lower()) or \
               ('permission' in content.lower() and 'denied' in content.lower()):
                print(f"  Access denied or not found for {dashboard_name}")
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
                # Create browser context
                context = await browser.new_context(
                    viewport={"width": self.width, "height": self.height}
                )

                # Create page
                page = await context.new_page()

                # Log in once
                login_success = await self.login(page)
                if not login_success:
                    print("ERROR: Could not log in to Luzmo")
                    return results

                # Capture each dashboard
                for i, dash in enumerate(dashboards, 1):
                    dashboard_id = dash.get('id', '')
                    dashboard_name = get_dashboard_name(dash)

                    print(f"Capturing {i}/{len(dashboards)}: {dashboard_name}")

                    screenshot_path = await self.capture_screenshot_async(
                        page,
                        dashboard_id,
                        dashboard_name,
                        wait_time=wait_time,
                        fullscreen=self.fullscreen,
                        debug=self.debug
                    )

                    results.append({
                        'id': dashboard_id,
                        'name': dashboard_name,
                        'screenshot_path': screenshot_path,
                        'success': screenshot_path is not None
                    })

                await page.close()
                await context.close()

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
                    context = await browser.new_context(
                        viewport={"width": self.width, "height": self.height}
                    )
                    page = await context.new_page()

                    # Log in
                    login_success = await self.login(page)
                    if not login_success:
                        print("ERROR: Could not log in to Luzmo")
                        return None

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
                    result = await self.capture_screenshot_async(
                        page,
                        dashboard_id,
                        dashboard_name,
                        wait_time,
                        fullscreen=self.fullscreen,
                        debug=self.debug
                    )

                    await page.close()
                    await context.close()
                    return result

                finally:
                    await browser.close()

        return asyncio.run(_capture())


def main():
    """Main function to capture dashboard screenshots with authentication."""
    capturer = DashboardScreenshotAuth()
    results = capturer.capture_all(limit=5)  # Test with 5 dashboards

    print("\nResults:")
    for r in results:
        status = "OK" if r['success'] else "FAILED"
        print(f"  [{status}] {r['name']}")


if __name__ == "__main__":
    main()
