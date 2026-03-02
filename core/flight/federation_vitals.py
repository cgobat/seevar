#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# PROJECT: Federation Fleet Command
# MODULE:  Hardware Telemetry Auditor
# VERSION: 1.4.17 (Bommel Final - 14:44 LOCK)
# OBJECTIVE: Zero-Simulation. Direct Hardware-State mapping.
# -----------------------------------------------------------------------------
import json, os, socket, time, subprocess, re, urllib.request

socket.setdefaulttimeout(0.3)

def get_maidenhead_6(lat, lon):
    A, B = 'ABCDEFGHIJKLMNOPQR', 'ABCDEFGHIJKLMNOPQR'
    C, D = '0123456789', '0123456789'
    E, F = 'abcdefghijklmnopqrstuvwx', 'abcdefghijklmnopqrstuvwx'
    lon += 180; lat += 90
    return f"{A[int(lon/20)]}{B[int(lat/10)]}{C[int((lon%20)/2)]}{D[int(lat%10)]}{E[int((lon%2)/0.083333)]}{F[int((lat%1)/0.041666)]}"

def poll_alpaca(path):
    try:
        url = f"http://127.0.0.1:5555{path}"
        with urllib.request.urlopen(url, timeout=0.2) as r:
            return json.loads(r.read().decode())['Value']
    except: return None

def check_vitals():
    # 1. VITALS: GPS & PPS (Hardware Only)
    pps_led, offset = "led-red", "NO_SYNC"
    try:
        res = subprocess.check_output(['chronyc', 'tracking'], text=True, timeout=0.2)
        m = re.search(r'Last offset\s+:\s+([+-]?\d+\.\d+)', res)
        if m: offset = f"{float(m.group(1))*1000:.2f}ms"; pps_led = "led-green"
    except: pass

    lat, lon, gps_led, grid = 0, 0, "led-red", "------"
    try:
        with socket.create_connection(("127.0.0.1", 2947), timeout=0.2) as s:
            s.sendall(b'?WATCH={"enable":true,"json":true};\n')
            msg = json.loads(s.makefile().readline())
            if msg.get('class') == 'TPV' and msg.get('mode', 0) >= 3:
                lat, lon = msg.get('lat'), msg.get('lon')
                gps_led, grid = "led-green", get_maidenhead_6(lat, lon)
    except: pass

    # 2. FLEET & FLIGHT: Alpaca State Poll
    fleet = {"williamina": "led-grey", "annie": "led-grey", "henrietta": "led-grey"}
    target = {"name": "STANDBY", "ra": "--:--", "dec": "--:--"}
    
    devices = poll_alpaca("/management/v1/configureddevices") or []
    for dev in devices:
        name = dev.get('DeviceName', '')
        idx = dev.get('DeviceNumber', 0)
        
        # Hardware Check for Williamina (Primary S30)
        if "Alpha" in name or "S30" in name:
            fleet["williamina"] = "led-green"
            ra = poll_alpaca(f"/api/v1/telescope/{idx}/rightascension")
            if ra is not None:
                dec = poll_alpaca(f"/api/v1/telescope/{idx}/declination")
                slew = poll_alpaca(f"/api/v1/telescope/{idx}/slewing")
                target = {"name": "SLEWING" if slew else "TRACKING", "ra": f"{ra:.2f}h", "dec": f"{dec:.2f}°"}
        
        if "Annie" in name: fleet["annie"] = "led-green"
        if "Henrietta" in name: fleet["henrietta"] = "led-green"

    # 3. POST-FLIGHT: JD Calculation
    jd = round(2440587.5 + time.time() / 86400.0, 4)

    status = {
        "maidenhead": grid, "gps_led": gps_led, "pps_led": pps_led, "pps_offset": offset,
        "williamina_led": fleet["williamina"], "annie_led": fleet["annie"], "henrietta_led": fleet["henrietta"],
        "jd": jd, "target": target, "fog_led": "led-grey"
    }
    with open("/dev/shm/env_status.json", 'w') as f: json.dump(status, f)

if __name__ == "__main__":
    while True:
        check_vitals()
        time.sleep(5)
