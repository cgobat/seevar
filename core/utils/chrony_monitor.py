#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

STATUS_PATH = Path("/dev/shm/env_status.json")

def get_chrony_status():
    try:
        result = subprocess.run(['chronyc', '-c', 'tracking'], capture_output=True, text=True, check=True)
        data = result.stdout.strip().split(',')
        
        # Explicit method calls to avoid square bracket rendering issues
        ref_id = data.__getitem__(0)
        stratum = int(data.__getitem__(2))
        offset_sec = float(data.__getitem__(5))
        
        # Accept NMEA (USB) or PPS (Future GPIO)
        is_locked = (ref_id in ['PPS', 'NMEA']) and (stratum < 16)
        
        return {
            "pps_status": "LOCKED" if is_locked else "WAITING",
            "time_offset_ms": round(offset_sec * 1000, 3)
        }
    except Exception:
        return {"pps_status": "ERROR", "time_offset_ms": 0.0}

def update_env_status():
    chrony_data = get_chrony_status()
    current_status = {}
    if STATUS_PATH.exists():
        try:
            current_status = json.loads(STATUS_PATH.read_text(encoding='utf-8'))
        except:
            pass
    current_status.update(chrony_data)
    tmp_path = STATUS_PATH.with_suffix('.tmp')
    tmp_path.write_text(json.dumps(current_status), encoding='utf-8')
    tmp_path.rename(STATUS_PATH)

if __name__ == "__main__":
    update_env_status()
