#!/usr/bin/env python3
"""
Check screenshots for loading spinners using Claude's vision capabilities.
"""

import os
import base64
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_screenshot_for_spinner(image_path: Path, client: Anthropic) -> dict:
    """
    Check if a screenshot contains a loading spinner.

    Args:
        image_path: Path to screenshot
        client: Anthropic client

    Returns:
        Dict with results
    """
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode('utf-8')

    # Ask Claude to analyze the image
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=150,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Does this screenshot show a loading spinner or loading indicator? Answer with just 'YES' or 'NO' and a brief explanation."
                    }
                ],
            }
        ],
    )

    response_text = message.content[0].text
    has_spinner = response_text.strip().upper().startswith('YES')

    return {
        'file': image_path.name,
        'has_spinner': has_spinner,
        'analysis': response_text
    }

def main():
    """Check all screenshots for loading spinners."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return

    client = Anthropic(api_key=api_key)

    screenshots_dir = Path('screenshots')

    if not screenshots_dir.exists():
        print(f"Error: {screenshots_dir} directory not found")
        return

    screenshots = sorted(screenshots_dir.glob('*.png'))

    if not screenshots:
        print(f"No screenshots found in {screenshots_dir}")
        return

    print(f"Checking {len(screenshots)} screenshots for loading spinners...")
    print("=" * 80)

    spinners_found = []

    for i, screenshot in enumerate(screenshots, 1):
        print(f"\n[{i}/{len(screenshots)}] Checking: {screenshot.name}")

        try:
            result = check_screenshot_for_spinner(screenshot, client)

            if result['has_spinner']:
                print(f"  [!] SPINNER DETECTED")
                print(f"  Analysis: {result['analysis']}")
                spinners_found.append(result)
            else:
                print(f"  [OK] No spinner detected")

        except Exception as e:
            print(f"  [ERROR] {str(e)}")

    # Summary
    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Total screenshots: {len(screenshots)}")
    print(f"  With spinners: {len(spinners_found)}")
    print(f"  OK: {len(screenshots) - len(spinners_found)}")

    if spinners_found:
        print(f"\n[!] Screenshots with loading spinners:")
        for result in spinners_found:
            print(f"  - {result['file']}")
        print(f"\nThese dashboards should be recaptured with --wait 10000 or higher")
    else:
        print(f"\n[OK] All screenshots look good!")

if __name__ == '__main__':
    main()
