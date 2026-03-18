 SeeVar — Installation Guide

> **Target platform:** Raspberry Pi (any model with 64-bit support)
> **Operating system:** Debian Bookworm 64-bit (Raspberry Pi OS)
> **Version:** 1.3.1

---

## What you need

| Item | Notes |
|------|-------|
| Raspberry Pi | Pi 4 or Pi 5 recommended |
| SD card | 16 GB minimum — OS only, no data stored here |
| 2 × USB drive | 256 GB or larger — RAID1 data archive |
| USB GPS receiver | Required for accurate timestamps and location |
| Seestar telescope | S30, S30-Pro, or S50 |

The telescope IP address does not need to be known at install time.
You can set it to `TBD` during the questionnaire and update `config.toml` later.

---

## Step 1 — Flash the SD card

Use **Raspberry Pi Imager 2.0** (or later).

1. Select **Raspberry Pi OS (64-bit)** — Bookworm
2. Click the **gear icon** (OS Customisation) before writing:

| Field | Value |
|-------|-------|
| Hostname | Your choice — e.g. `seevar`, `observatory`, `mypi` |
| Enable SSH | ✓ — Use password authentication |
| Username | Your chosen username (e.g. `ed`) |
| Password | Set a strong password |
| Locale / timezone | Set to your location |
| WiFi | Set if connecting wirelessly |

3. Write the card, insert into Pi, power on.

---

## Step 2 — First SSH connection

Wait ~60 seconds for first boot, then:

```bash
ssh <username>@<hostname>.local
Step 3 — Enable passwordless sudoBootstrap requires passwordless sudo for system package installation.Bashecho "$(whoami) ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/seevar
Step 4 — Run bootstrapBashcurl -fsSL [https://raw.githubusercontent.com/edjuh/seevar/main/bootstrap.sh](https://raw.githubusercontent.com/edjuh/seevar/main/bootstrap.sh) | bash
Or if you prefer to inspect it first:Bashwget [https://raw.githubusercontent.com/edjuh/seevar/main/bootstrap.sh](https://raw.githubusercontent.com/edjuh/seevar/main/bootstrap.sh)
less bootstrap.sh
bash bootstrap.sh
Bootstrap will:Install system packages via aptClone the repository to ~/seevarCreate a Python virtual environment at ~/seevar/.venvInstall all Python dependenciesRun the telescope questionnaire — model, name, IPRun the site questionnaire — AAVSO credentials, location, optional Telegram and NASCreate the data directory structure and seed empty state filesInstall and enable the four user-level systemd services (Dashboard, Orchestrator, Weather, GPS)Run a sanity checkPrint a summaryTotal time: approximately 10–15 minutes on a Pi 5, longer on a Pi 4(Python dependency build includes compiled packages).Step 5 — Set telescope IPOnce your telescope is on the network, find its IP address in the Seestar appor your router's DHCP table. Then edit config.toml:Ini, TOML[[seestars]]
name  = "Wilhelmina"
model = "S30-Pro"
ip    = "192.168.1.x"     # ← set this
mount = "altaz"
Then regenerate the fleet schema:Bashcd ~/seevar
python3 core/hardware/fleet_mapper.py
Step 6 — Run chart_fetcher overnightThe seed catalog bundled with SeeVar contains 442 targets and reference starsfor 40°–60°N. It is sufficient to start observing immediately.To refresh or expand the catalog, run the chart fetcher once.This is a slow process (~3.14m/query) due to AAVSO API throttling !!! — run it overnight:Bashcd ~/seevar
python3 core/preflight/chart_fetcher.py
Step 7 — Managing the observatorySeeVar runs as user-level systemd services. Use the --user flag to manage them:Bashsystemctl --user status seevar-orchestrator
systemctl --user stop seevar-weather
systemctl --user restart seevar-dashboard
Dashboard: http://<hostname>.local:5050Astrometry.net index filesPlate solving requires index files matched to your telescope's field of view.These are not included in the repository.ModelFOVRecommended index filesS30~4.5°index-4107 to index-4110S30-Pro~4.0°index-4107 to index-4110S50~2.5°index-4108 to index-4111Install via apt:Bashsudo apt install astrometry-data-tycho2-10-19
Or download directly from: http://data.astrometry.net/4100/Configuration reference~/seevar/config.toml — all runtime settings.~/seevar/config.toml.example — annotated template.Key settings after install:SettingLocationDefaultNotesobserver_code[aavso]—Your AAVSO code — required for submissionssimulation_mode[planner]falseSet true for dry runs without hardwareip[[seestars]]TBDTelescope IP — update when knowntelegram_bot_token[notifications]""Optional session alertsnas_ip[network]""Optional NAS archiveLogs~/seevar/logs/orchestrator.log
~/seevar/logs/dashboard.log
~/seevar/logs/weather.log
~/seevar/logs/gps.log
Uninstall / reinstallTo start fresh on the same SD card:Bashsystemctl --user stop seevar-dashboard seevar-orchestrator seevar-weather seevar-gps
systemctl --user disable seevar-dashboard seevar-orchestrator seevar-weather seevar-gps
rm ~/.config/systemd/user/seevar-*.service
systemctl --user daemon-reload
rm -rf ~/seevar
Then re-run bootstrap from Step 4.
