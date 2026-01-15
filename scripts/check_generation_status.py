#!/usr/bin/env python3
"""
Quick status checker for synthetic data generations.
Shows active checkpoints, completed files, and running processes.
"""

import json
from pathlib import Path
from datetime import datetime
import subprocess

def check_checkpoints():
    """Check for active checkpoints."""
    checkpoint_dir = Path("data/checkpoints")

    if not checkpoint_dir.exists():
        return []

    checkpoints = []
    for cp_file in checkpoint_dir.glob("*_checkpoint.json"):
        try:
            with open(cp_file) as f:
                data = json.load(f)
            checkpoints.append(data)
        except Exception as e:
            print(f"Warning: Could not read {cp_file}: {e}")

    return checkpoints

def check_completed_files():
    """Check recently completed synthetic files."""
    synthetic_dir = Path("data/synthetic/kantar")

    if not synthetic_dir.exists():
        return []

    files = []
    for xlsx_file in synthetic_dir.glob("*/US/synthetic_*.xlsx"):
        stat = xlsx_file.stat()
        files.append({
            'path': str(xlsx_file),
            'study_id': xlsx_file.parts[-3],
            'size_kb': stat.st_size / 1024,
            'modified': datetime.fromtimestamp(stat.st_mtime)
        })

    # Sort by modification time, newest first
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files

def check_running_processes():
    """Check for running generation processes."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )

        processes = []
        for line in result.stdout.split('\n'):
            if 'python' in line.lower() and ('generate' in line or 'quick-gen' in line):
                if 'grep' not in line and 'check_generation_status' not in line:
                    processes.append(line.strip())

        return processes
    except Exception as e:
        print(f"Warning: Could not check processes: {e}")
        return []

def main():
    print("=" * 70)
    print("SYNTHETIC DATA GENERATION STATUS")
    print("=" * 70)

    # Check active checkpoints
    checkpoints = check_checkpoints()
    print(f"\n📊 ACTIVE CHECKPOINTS ({len(checkpoints)}):")
    if checkpoints:
        for cp in checkpoints:
            progress_pct = cp.get('progress_pct', 0)
            completed = cp.get('completed', 0)
            total = cp.get('total', 0)
            job_id = cp.get('job_id', 'unknown')
            timestamp = cp.get('checkpoint_time', 'unknown')

            print(f"\n  • {job_id}")
            print(f"    Progress: {completed}/{total} respondents ({progress_pct:.1f}%)")
            print(f"    Last saved: {timestamp}")
            print(f"    Resume: python3 -m src.cli.main generate study ... --resume")
    else:
        print("  None - all generations complete or not started")

    # Check running processes
    processes = check_running_processes()
    print(f"\n🔄 RUNNING PROCESSES ({len(processes)}):")
    if processes:
        for proc in processes:
            # Extract just the relevant part
            if 'src.cli.main' in proc:
                cmd_start = proc.find('src.cli.main')
                cmd = proc[cmd_start:cmd_start+100] + '...'
                print(f"  • {cmd}")
    else:
        print("  None - no active generations")

    # Check completed files
    completed = check_completed_files()
    print(f"\n✓ COMPLETED FILES (US market, last 5):")
    if completed:
        for i, file in enumerate(completed[:5], 1):
            study = file['study_id']
            age = datetime.now() - file['modified']

            if age.days > 0:
                age_str = f"{age.days}d ago"
            elif age.seconds > 3600:
                age_str = f"{age.seconds//3600}h ago"
            else:
                age_str = f"{age.seconds//60}m ago"

            print(f"  {i}. {study} - {file['size_kb']:.0f}KB - {age_str}")
    else:
        print("  None - no synthetic files found")

    print("\n" + "=" * 70)
    print("\nQuick Commands:")
    print("  Resume: python3 -m src.cli.main generate study <STUDY_ID> US -n 50 --resume")
    print("  Check this status: python3 scripts/check_generation_status.py")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
