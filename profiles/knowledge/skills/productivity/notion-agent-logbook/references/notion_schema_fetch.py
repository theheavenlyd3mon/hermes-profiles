#!/usr/bin/env python3
"""
Fetch Notion database schema and print property names by type.
Handles both top-level properties and data_sources pattern.
"""
import subprocess, json, os, sys

def get_api_key():
    """Read NOTION_API_KEY from ~/.hermes/.env or environment."""
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("NOTION_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not api_key:
        print("Error: NOTION_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    return api_key

def curl(url, api_key):
    """Run curl and return parsed JSON."""
    r = subprocess.run(["curl", "-s", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Notion-Version: 2025-09-03"],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Error: curl failed: {r.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(r.stdout)

def main(db_id=None):
    if not db_id:
        if len(sys.argv) < 2:
            print("Usage: python3 notion_schema_fetch.py <database_id>", file=sys.stderr)
            sys.exit(1)
        db_id = sys.argv[1]

    api_key = get_api_key()

    # Fetch database
    data = curl(f"https://api.notion.com/v1/databases/{db_id}", api_key)

    # Try top-level properties first
    props = data.get("properties", {})
    if props:
        print("=== Top-level properties (legacy pattern) ===")
        for k, v in props.items():
            print(f"  {repr(k)} -> {v.get('type', '?')}")
        return

    # Try data_sources pattern
    ds_list = data.get("data_sources", [])
    if not ds_list:
        # Check if we got a valid response at all — if not, the ID might be wrong
        if not data or data.get("object") == "error":
            print("Error: Notion API returned an error for this database ID.", file=sys.stderr)
            print(f"  Make sure you're passing the DATABASE ID (not data source ID).", file=sys.stderr)
            print(f"  Database ID: looks like a UUID in the Notion page URL after the workspace name.", file=sys.stderr)
            sys.exit(1)
        print("Error: No properties or data_sources found", file=sys.stderr)
        print("  Tip: If you passed a data source ID by mistake, use the database ID instead.", file=sys.stderr)
        sys.exit(1)

    print("=== Data source properties (new pattern) ===")
    for ds in ds_list:
        ds_id = ds.get("id")
        ds_name = ds.get("name", "?")
        print(f"\nData source: {ds_id} ({ds_name})")

        ds_data = curl(f"https://api.notion.com/v1/data_sources/{ds_id}", api_key)
        props = ds_data.get("properties", {})
        for k, v in props.items():
            print(f"  {repr(k)} -> {v.get('type', '?')}")

if __name__ == "__main__":
    main()
