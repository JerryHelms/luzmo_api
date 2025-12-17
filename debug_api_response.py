#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to see the actual API response from Luzmo.
"""

from src.luzmo_client import LuzmoClient
import json
import sys
import io

# Fix Windows console encoding for unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    print("="*80)
    print("Luzmo API Response Debugger")
    print("="*80)

    try:
        client = LuzmoClient()
        print("\n✓ Client initialized\n")

        print("Making API request to list dashboards...")
        print("URL:", f"{client.host}/{client.api_version}/securable")
        print("\nPayload:")
        payload = {
            'action': 'get',
            'version': client.api_version,
            'key': client.api_key[:10] + '...',  # Hide most of the key
            'token': client.api_token[:10] + '...',  # Hide most of the token
            'find': {
                'where': {
                    'type': 'dashboard',
                    'derived': False
                },
                'attributes': ['id', 'name', 'description', 'modified_at'],
                'order': [['modified_at', 'desc']]
            }
        }
        print(json.dumps(payload, indent=2))

        # Get the actual response
        response = client._make_request(
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

        print("\n" + "="*80)
        print("RAW API RESPONSE:")
        print("="*80)
        print(json.dumps(response, indent=2))

        print("\n" + "="*80)
        print("RESPONSE ANALYSIS:")
        print("="*80)
        print(f"Response type: {type(response)}")
        print(f"Response is list: {isinstance(response, list)}")
        print(f"Response is dict: {isinstance(response, dict)}")

        if isinstance(response, dict):
            print(f"\nResponse keys: {list(response.keys())}")

            if 'data' in response:
                print(f"'data' key exists: {type(response['data'])}")
                print(f"Length of data: {len(response['data']) if isinstance(response['data'], list) else 'N/A'}")

            # Check for other common keys
            for key in ['results', 'items', 'dashboards', 'securables']:
                if key in response:
                    print(f"'{key}' key exists: {type(response[key])}")
                    print(f"Length of {key}: {len(response[key]) if isinstance(response[key], list) else 'N/A'}")

        print("\n" + "="*80)
        print("CURRENT list_dashboards() LOGIC:")
        print("="*80)
        print("Returns: response if isinstance(response, list) else response.get('data', [])")

        result = response if isinstance(response, list) else response.get('data', [])
        print(f"\nCurrent logic returns: {type(result)}")
        print(f"Length: {len(result) if isinstance(result, list) else 'N/A'}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
