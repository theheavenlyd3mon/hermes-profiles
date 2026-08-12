#!/usr/bin/env python3
"""Dojo nightly count — aggregate daily work across sources and log to Notion."""

from pathlib import Path
from datetime import datetime, timedelta
import subprocess, json, os, sys

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"=== Dojo Nightly Count — {today} ===\n")
    
    completed = 0
    stalled = []
    details = []
    
    # 1. Obsidian daily notes
    obsidian_path = Path("~/Hermes Vault/Hermes/Daily Notes")
    print("1. Obsidian Daily Notes:")
    if obsidian_path.exists():
        daily = obsidian_path / today
        if daily.exists() and daily.is_dir():
            md_files = list(daily.glob("*.md"))
            if md_files:
                print(f"   Found {len(md_files)} entries in {today}/")
                for f in md_files:
                    content = f.read_text()
                    if "done" in content.lower() or "✅" in content or "completed" in content.lower() or "✓" in content:
                        completed += 1
                print(f"   → Completed tasks: {completed}")
            else:
                print(f"   No daily notes found for {today}")
        else:
            print(f"   No daily notes found for {today}")
    else:
        print("   Obsidian vault path not found")
    
    # 2. Notion database
    print("\n2. Notion Agent Logbook:")
    db_id = "9dc914a6-6736-40af-a0b9-d1af9fc5e8a1"
    api_key = os.environ.get("NOTION_API_KEY")
    
    if api_key:
        result = subprocess.run([
            "curl", "-s", f"https://api.notion.com/v1/databases/{db_id}/query",
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Notion-Version: 2025-09-03",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"filter": {"property": "Date", "date": {"on_or_after": today}}})
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            results = data.get("results", [])
            print(f"   Found {len(results)} entries since {today}")
            for entry in results:
                props = entry.get("properties", {})
                name = props.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")
                status = props.get("Status", {}).get("select", {}).get("name", "Unknown")
                agent = props.get("Agent", {}).get("select", {}).get("name", "Unknown")
                details.append(f"{agent}: {name} ({status})")
                if status == "completed":
                    completed += 1
                elif status in ["pending", "failed"]:
                    stalled.append(f"{agent}: {name}")
        else:
            print(f"   API error: {result.stderr[:200]}")
    else:
        print("   NOTION_API_KEY not set")
    
    # 3. Cron jobs
    print("\n3. Cron Jobs:")
    result = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        print(f"   Total cron jobs: {len(lines) - 2}")
        for line in lines:
            if 'error' in line:
                stalled.append(f"cron: {line.split()[0]} ({line.split()[-1]})")
    else:
        print("   Could not retrieve cron list")
    
    # 4. Kanban
    print("\n4. Kanban Board:")
    result = subprocess.run(["hermes", "kanban", "list"], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        done = blocked = 0
        for line in lines:
            if line.startswith('✓'):
                done += 1
            elif 'blocked' in line.lower() or 'stalled' in line.lower():
                blocked += 1
                stalled.append(f"kanban: {line}")
        completed += done
        print(f"   Completed: {done}, Blocked/Stalled: {blocked}")
    else:
        print("   Could not retrieve kanban list")
    
    # Summary
    print("\n" + "="*50)
    print(f"SUMMARY — {today}")
    print("="*50)
    print(f"Total completed: {completed}")
    print(f"Stalled/blocked items: {len(stalled)}")
    if stalled:
        print("\nStalled items:")
        for item in stalled[:10]:
            print(f"  • {item}")
    
    # Log to Notion
    print("\nLogging to Notion Agent Logbook...")
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Name": {"title": [{"text": {"content": f"Dojo nightly: {today}"}}]},
            "Agent": {"select": {"name": "cron"}},
            "Type": {"select": {"name": "session"}},
            "Date": {"date": {"start": today}},
            "Status": {"select": {"name": "completed"}},
            "Tags": {"multi_select": [{"name": "dojo"}, {"name": "daily"}]},
            "Cost": {"number": 0.0},
            "Summary": {"rich_text": [{"text": {"content": f"Completed tasks: {completed}\nStalled/blocked: {len(stalled)}\n\nDetails: {len(details)} entries in logbook\n\nStalled items:\n" + "\n".join(f"• {s}" for s in stalled[:10])}}]}
        }
    }
    
    if api_key:
        log_result = subprocess.run([
            "curl", "-s", "-X", "POST", "https://api.notion.com/v1/pages",
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Notion-Version: 2025-09-03",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ], capture_output=True, text=True)
        
        if log_result.returncode == 0:
            print("✓ Logged to Notion successfully")
        else:
            print(f"✗ Notion log failed: {log_result.stderr[:200]}")
    else:
        print("⚠ NOTION_API_KEY not set — skipped logging")

if __name__ == "__main__":
    main()
