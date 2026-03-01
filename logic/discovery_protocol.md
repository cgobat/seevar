# 🛰️ Discovery Protocol (v1.4 Kriel)

## Objective
To transition the observatory from a static "Home" configuration to a dynamic "Field" state based on environmental audit at boot-up.

## 1. Network Discovery & AP Fallback
* **Home Check:** At boot, the system checks for an IP in the `192.168.178.0/24` range.
* **Status:** * If `True`: Set `PROFILE=HOME`, mount NAS `/mnt/astronas/`.
    * If `False`: Set `PROFILE=FIELD`, bypass NAS, route storage to `lifeboat_dir`.
* **AP Trigger:** If no WiFi connection is established after 180 seconds, the system invokes `nmcli` to host a "Seestar_Sentry_AP". The Dashboard is served at `10.42.0.1`.



## 2. Temporal Alignment (GPS PPS)
* **Pre-Flight Requirement:** Before any observations, the system must sync with the GPS Atomic Clock.
* **Execution:** Use `chrony` to prefer the PPS signal from `/dev/pps0`.
* **Gate:** Pre-flight fails if system clock offset > 0.5s from GPS time.

## 3. Positional Awareness (In-Memory)
* **Persistence:** NO physical writes to `config.toml` for coordinates during a session.
* **Storage:** All live GPS data (Lat, Lon, Alt, Maidenhead) must be stored in `/dev/shm/discovery.json`.
* **Precision:** Display 6-character Maidenhead (e.g., JO22hj) on the Dashboard as the "Live Pulse."
* **Write-Back:** Only write to `config.toml` upon a successful manual "Confirm Site" action from the Dashboard.

## 4. Storage Sentinel (85% Gate)
* **Monitoring:** Continuous check of the filesystem where `lifeboat_dir` resides.
* **Action:** If disk usage exceeds 85%, the `sync_manager.py` must halt FITS acquisition and only allow metadata (.json/.csv) reports to be generated.
