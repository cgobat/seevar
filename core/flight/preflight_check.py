#!/usr/bin/env python3
import json, os, socket, time, subprocess, re, tomllib, urllib.request

def get_maidenhead_6(lat, lon):
    A, B = 'ABCDEFGHIJKLMNOPQR', 'ABCDEFGHIJKLMNOPQR'
    C, D = '0123456789', '0123456789'
    E, F = 'abcdefghijklmnopqrstuvwx', 'abcdefghijklmnopqrstuvwx'
    lon += 180; lat += 90
    return f"{A[int(lon/20)]}{B[int(lat/10)]}{C[int((lon%20)/2)]}{D[int(lat%10)]}{E[int((lon%2)/0.083333)]}{F[int((lat%1)/0.041666)]}"

def check_vitals():
    cfg_path = "/home/ed/seestar_organizer/config.toml"
    with open(cfg_path, "rb") as f: cfg = tomllib.load(f)
    
    # GPS Logic
    gps_led, lat, lon = "led-orange", 0.0, 0.0
    try:
        with socket.create_connection(("127.0.0.1", 2947), timeout=0.5) as s:
            s.sendall(b'?WATCH={"enable":true,"json":true};\n')
            msg = json.loads(s.makefile().readline())
            if msg.get('class') == 'TPV' and msg.get('mode', 0) >= 3:
                gps_led, lat, lon = "led-green", msg.get('lat'), msg.get('lon')
    except: pass

    if lat == 0.0:
        lat, lon = cfg['location'].get('lat', 52.382), cfg['location'].get('lon', 4.601)
    
    # 🌉 Fleet Injection (Port 5555 Handshake)
    fleet = {"Williamina": "led-grey", "Annie": "led-grey", "Henrietta": "led-grey"}
    try:
        with urllib.request.urlopen("http://127.0.0.1:5555/management/v1/configureddevices", timeout=0.5) as r:
            devices = json.loads(r.read().decode()).get('Value', [])
            for dev in devices:
                d_name = dev.get('DeviceName', '')
                if "Alpha" in d_name or "Williamina" in d_name: fleet["Williamina"] = "led-green"
                if "Annie" in d_name: fleet["Annie"] = "led-green"
                if "Henrietta" in d_name: fleet["Henrietta"] = "led-green"
    except: pass

    # Time/PPS
    try:
        res = subprocess.check_output(['chronyc', 'tracking'], text=True, timeout=1)
        offset = f"{float(re.search(r'Last offset\s+:\s+([+-]?\d+\.\d+)', res).group(1))*1000:.2f}ms"
        pps_led = "led-green"
    except: pps_led, offset = "led-red", "WAIT"

    status = {
        "maidenhead": get_maidenhead_6(lat, lon), # Requirement #3: Just the 6 chars
        "gps_led": gps_led,
        "pps_led": pps_led,
        "pps_offset": offset,
        "williamina_led": fleet["Williamina"],
        "annie_led": fleet["Annie"],
        "henrietta_led": fleet["Henrietta"],
        "fog_led": "led-grey",
        "jd": round(2440587.5 + time.time() / 86400.0, 4)
    }
    with open("/dev/shm/env_status.json", 'w') as f: json.dump(status, f)

if __name__ == "__main__":
    while True:
        try: check_vitals()
        except: pass
        time.sleep(5)
