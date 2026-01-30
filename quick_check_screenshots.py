#!/usr/bin/env python3
"""
Quick heuristic check for potentially problematic screenshots.
"""

from pathlib import Path
from PIL import Image
import sys

def check_screenshot_heuristics(image_path: Path) -> dict:
    """
    Check screenshot using quick heuristics.

    Args:
        image_path: Path to screenshot

    Returns:
        Dict with results
    """
    try:
        img = Image.open(image_path)
        file_size = image_path.stat().st_size

        # Get image properties
        width, height = img.size

        # Check for uniform/simple images (potential loading screens)
        # Convert to RGB for analysis
        img_rgb = img.convert('RGB')

        # Sample pixels to check for uniformity
        pixels = list(img_rgb.getdata())
        unique_colors = len(set(pixels[:1000]))  # Sample first 1000 pixels

        # Heuristics for potential issues
        is_suspicious = False
        reasons = []

        # Very small file for the resolution (compressed/simple)
        expected_min_size = (width * height) / 50  # Very rough heuristic
        if file_size < expected_min_size:
            is_suspicious = True
            reasons.append(f"Small file size ({file_size:,} bytes)")

        # Very few unique colors in sample
        if unique_colors < 50:
            is_suspicious = True
            reasons.append(f"Low color variety ({unique_colors} unique colors in sample)")

        return {
            'file': image_path.name,
            'file_size': file_size,
            'dimensions': f"{width}x{height}",
            'unique_colors_sample': unique_colors,
            'is_suspicious': is_suspicious,
            'reasons': reasons
        }
    except Exception as e:
        return {
            'file': image_path.name,
            'error': str(e)
        }

def main():
    """Quick check all screenshots."""
    screenshots_dir = Path('screenshots')

    if not screenshots_dir.exists():
        print(f"Error: {screenshots_dir} directory not found")
        return

    screenshots = sorted(screenshots_dir.glob('*.png'))

    if not screenshots:
        print(f"No screenshots found in {screenshots_dir}")
        return

    print(f"Quick checking {len(screenshots)} screenshots...")
    print("=" * 80)

    suspicious = []
    errors = []

    for i, screenshot in enumerate(screenshots, 1):
        result = check_screenshot_heuristics(screenshot)

        if 'error' in result:
            errors.append(result)
            print(f"[{i}/{len(screenshots)}] ❌ {result['file']}: {result['error']}")
        elif result['is_suspicious']:
            suspicious.append(result)
            print(f"[{i}/{len(screenshots)}] ⚠️  {result['file']}")
            for reason in result['reasons']:
                print(f"    - {reason}")
        else:
            # Only print every 10th OK result to reduce noise
            if i % 10 == 0 or i == len(screenshots):
                print(f"[{i}/{len(screenshots)}] ✓ {result['file']}")

    # Summary
    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Total screenshots: {len(screenshots)}")
    print(f"  Suspicious: {len(suspicious)}")
    print(f"  OK: {len(screenshots) - len(suspicious) - len(errors)}")
    print(f"  Errors: {len(errors)}")

    if suspicious:
        print(f"\n⚠️  Suspicious screenshots (may have loading spinners):")
        for result in suspicious:
            print(f"  - {result['file']}")
            print(f"    Size: {result['file_size']:,} bytes, Colors: {result['unique_colors_sample']}")
        print(f"\nRecommendation: Use check_spinner_screenshots.py to verify these with Claude vision API")

    if errors:
        print(f"\n❌ Screenshots with errors:")
        for result in errors:
            print(f"  - {result['file']}: {result['error']}")

if __name__ == '__main__':
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow library not installed")
        print("Install with: pip install Pillow")
        sys.exit(1)

    main()
