#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def stake_zombie():
    # Use the path provided by 'which python3' in your terminal
    venv_path = Path("/home/ed/.pyenv/shims/python3")
    lock_path = Path("/home/ed/seestar_organizer/logs/env_verified.lock")
    
    # Pillar Check: Does the pyenv shim exist?
    if not venv_path.exists():
        print(f"❌ VENV MISSING: {venv_path}")
        sys.exit(1)
        
    try:
        # Ensure the logs directory exists
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        # Stake the ground: Ensure logs are writable
        with open(lock_path, 'w') as f:
            f.write(f"Verified at {os.uname().nodename}")
        print("✅ Environment Secured. Lock file created.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ PERMISSION ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    stake_zombie()
