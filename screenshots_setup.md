# Dashboard Screenshots Setup

This module uses Playwright to capture screenshots of Luzmo dashboards.

## Prerequisites

1. **Install Playwright:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

## Choose Your Authentication Method

You have **three options** for capturing screenshots:

### Option A: Authenticated Login (Recommended - No Embed Required)

Uses your regular Luzmo login credentials via Playwright automation.

**Pros:**
- No embed configuration needed
- Works for all dashboards you have access to
- Most straightforward setup

**Cons:**
- Requires login credentials
- Login form selectors may need adjustment if Luzmo updates UI

**Setup:**
```bash
# Set environment variables
set LUZMO_EMAIL=your-email@example.com
set LUZMO_PASSWORD=your-password

# Capture screenshots
python capture_screenshots_auth.py --limit 10
```

**Usage:**
```bash
# Capture all dashboards
python capture_screenshots_auth.py

# Capture specific dashboard
python capture_screenshots_auth.py --dashboard YOUR_DASHBOARD_ID

# Limit to 10 dashboards
python capture_screenshots_auth.py --limit 10

# Pass credentials directly (not recommended for scripts)
python capture_screenshots_auth.py --email user@example.com --password yourpass
```

---

### Option B: Embed Access

Uses Luzmo's embed API (choose one sub-option):

#### Option B1: Dynamic Authorization

Enable embed access in your Luzmo account:
1. Go to Luzmo Settings > Integrations
2. Enable "Embed" integration
3. The API will then be able to create authorization tokens dynamically

**Pros:** Secure, token-based auth
**Cons:** Requires embed integration enabled

#### Option B2: Pre-generated Embed Credentials

If you have static embed credentials, add them to your `.env`:
```
LUZMO_EMBED_KEY=your-embed-key
LUZMO_EMBED_TOKEN=your-embed-token
```

**Pros:** No login required
**Cons:** Requires manual embed credential setup

---

### Option C: Public Dashboard Sharing

Enable public sharing on individual dashboards:
1. Open dashboard in Luzmo
2. Click Share > Public Link
3. This generates a slug for public access

**Pros:** No auth needed
**Cons:** Only works for publicly shared dashboards

## Quick Comparison

| Method | Auth Required | Setup Difficulty | Works For |
|--------|--------------|------------------|-----------|
| **Authenticated Login** | Login credentials | Easy | All accessible dashboards |
| **Embed (Dynamic)** | Embed integration | Medium | All dashboards |
| **Embed (Static)** | Embed credentials | Medium | All dashboards |
| **Public URL** | None | Easy | Public dashboards only |

## Usage Examples

### Using Authenticated Login (No Embed)

```bash
# Set credentials
set LUZMO_EMAIL=your-email@example.com
set LUZMO_PASSWORD=your-password

# Capture all dashboards
python capture_screenshots_auth.py

# Capture specific dashboard
python capture_screenshots_auth.py --dashboard YOUR_DASHBOARD_ID

# Limit to 10 dashboards
python capture_screenshots_auth.py --limit 10
```

### Using Embed Access

```bash
# Capture all dashboards
python capture_screenshots.py

# Capture specific dashboard
python capture_screenshots.py --dashboard YOUR_DASHBOARD_ID

# Limit to 10 dashboards
python capture_screenshots.py --limit 10

# Custom output directory
python capture_screenshots.py --output my_screenshots

# Custom viewport
python capture_screenshots.py --width 1280 --height 720

# Longer wait time for complex dashboards
python capture_screenshots.py --wait 10000
```

## Output

Screenshots are saved to the `screenshots/` directory (or custom directory) with filenames:
```
Dashboard_Name_abc12345.png
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not create embed authorization" | Embed not enabled | Enable embed integration in Luzmo Settings |
| "Access denied" | No permission | Check dashboard permissions or enable public sharing |
| Blank screenshots | Dashboard didn't load | Increase `--wait` time |
| Timeout | Network issues | Check connectivity to Luzmo |

## Without Embed Access

If you cannot configure embed access, alternatives include:
1. **Manual screenshots** - Take screenshots directly in Luzmo UI
2. **Scheduled exports** - Use Luzmo's built-in email export feature
3. **Browser extension** - Use a screenshot extension while logged into Luzmo

## API Reference

### Using Authenticated Login

```python
from src.dashboard_screenshot_auth import DashboardScreenshotAuth

# Initialize with credentials
capturer = DashboardScreenshotAuth(
    output_dir='screenshots',
    width=1920,
    height=1080,
    email='your-email@example.com',  # Or set LUZMO_EMAIL env var
    password='your-password'          # Or set LUZMO_PASSWORD env var
)

# Capture single dashboard
path = capturer.capture_single('dashboard-id')

# Capture all dashboards
results = capturer.capture_all(limit=10, wait_time=5000)
```

### Using Embed Access

```python
from src.dashboard_screenshot import DashboardScreenshot

# Initialize
capturer = DashboardScreenshot(
    output_dir='screenshots',
    width=1920,
    height=1080,
    embed_key='optional-key',      # Or set LUZMO_EMBED_KEY env var
    embed_token='optional-token'   # Or set LUZMO_EMBED_TOKEN env var
)

# Capture single dashboard
path = capturer.capture_single('dashboard-id')

# Capture all dashboards
results = capturer.capture_all(limit=10, wait_time=5000)
```
