# Seestar Organizer: Purified Manifest

## 🛫 PREFLIGHT
* `core/preflight/asassn_validator.py`: Queries ASAS-SN for current magnitudes to ensure targets are within the S30-Pro's 30mm aperture limits (Mag 7.5 - 13.0).
* `core/preflight/audit.py`: Tags done objects until new observation is required based on cadence.
* `core/preflight/fetcher.py`: Fetches AAVSO data with query-string auth and a file-lock to prevent collisions.
* `core/preflight/fog_monitor.py`: Infrared sky-clarity monitor using MLX90614 to prevent imaging in fog.
* `core/preflight/gps.py`: Manages geographic coordinates using config.toml as the source of truth.
* `core/preflight/harvester.py`: Downloads active campaigns from AAVSO, vetoing targets outside FOV constraints and enforcing path resolution via config.toml.
* `core/preflight/horizon.py`: Veto targets based on local obstructions (Trees, Buildings) using Az/Alt mapping.
* `core/preflight/librarian.py`: Monthly cron tool to fetch NEW targets from AAVSO.
* `core/preflight/nightly_planner.py`: Generates prioritized target lists based on real-time altitude, scientific urgency, and AAVSO cadence requirements.
* `core/preflight/preflight_master.py`: Orchestrates sequential fetching, coordinate normalization,
* `core/preflight/target_evaluator.py`: Audits the nightly plan for freshness and quantity.
* `core/preflight/weather.py`: Calculates astronomical dark, fetches Open-Meteo & Buienradar forecasts, and returns a UTF-8 evaluated status.
* `core/planning/nightly_planner.py`: Score 1,240 targets against tonights sky and pick the Top 20.

## 🚀 FLIGHT
* `core/flight/block_injector.py`: Transforms tonights_plan.json into 15-minute science blocks using config-driven coordinates.
* `core/flight/env_loader.py`: Centralized configuration and environment variable manager.
* `core/flight/fill_the_night.py`: Stress-test utility to saturate the Federation schedule for maximum night capacity.
* `core/flight/flight-to-post-handover.py`: Secures data after a mission, stops hardware bridges, and triggers post-flight analysis workflows.
* `core/flight/get_manifest.py`: Human-readable reporter for the current Alpaca Bridge flight schedule.
* `core/flight/hardware_profiles.py`: Define sensor specs for Annie (S50), Williamina (S30-Pro), and Henrietta (S30-Pro Fast).
* `core/flight/orchestrator.py`: Primary flight control daemon that manages hardware states (Slewing, Centering, Integrating) and broadcasts telemetry to the dashboard.
* `core/flight/preflight_check.py`: Executes full system validation including Targets, GPS, Bridge, Weather, and Disk.
* `core/flight/sequence_engine.py`: Prioritizes targets without crashing on vault attributes.
* `core/flight/vault_manager.py`: Manages secure access to observational metadata and synchronizes GPS coordinates with config.toml.

## 🧪 POSTFLIGHT
* `core/postflight/analyst.py`: Analyzes FITS image quality, FWHM, and basic observational metrics.
* `core/postflight/analyzer.py`: Validates FITS headers and calculates basic QC metrics.
* `core/postflight/calibration_engine.py`: Manages Zero-Point (ZP) offsets and flat-field corrections for the IMX585.
* `core/postflight/master_analyst.py`: High-level plate-solving coordinator for narrow-field Seestar frames.
* `core/postflight/notifier.py`: Outbound alert management via Telegram and system bells.
* `core/postflight/pastinakel_math.py`: Logic for saturation detection and dynamic aperture scaling.
* `core/postflight/photometry_engine.py`: Instrumental flux extraction and science-grade lightcurve generation.
* `core/postflight/pixel_mapper.py`: Converts celestial WCS coordinates to local sensor pixel X/Y coordinates.
* `core/postflight/post_to_pre_feedback.py`: Updates the master targets.json with successful observation dates extracted from QC reports.
* `core/postflight/sync_manager.py`: Manages file synchronization between Seestar, Local Buffer, and NAS.

## 🛠️ UTILS
* `utils/aavso_client.py`: Low-level API client for authenticated AAVSO VSX and WebObs data retrieval.
* `utils/astro.py`: Core library for RA/Dec parsing, sidereal time, and coordinate math.
* `utils/audit_setup.py`: Dumps current Horizon and Target configuration for architectural review.
* `utils/auto_header.py`: Injects standardized file headers into Python scripts across the project.
* `utils/campaign_auditor.py`: Unpacks the JSON envelope and cross-references campaign targets with available AAVSO comparison charts via coordinates.
* `utils/campaign_cleaner.py`: Deduplicates root campaign targets and securely links them via robust coordinate parsing.
* `utils/check_headers.py`: Utility to verify all project Python files contain a standardized PEP 257 header.
* `utils/cleanup.py`: Housekeeping utility for purging temporary files and rotating stale logs to prevent storage bloat.
* `utils/comp_purger.py`: Scans comparison charts and deletes any file that is empty, malformed, or missing coordinate data.
* `utils/coordinate_converter.py`: Ensures data validity by converting sexagesimal AAVSO coordinates into decimal degrees for internal computational use and plate-solving.
* `utils/fix_imports.py`: Automated namespace correction utility for project-wide absolute import resolution.
* `utils/generate_manifest.py`: Captures full-sentence objectives without clipping and syncs the resulting manifest to the NAS.
* `utils/ghost_photometry.py`: Diagnostic tool for identifying internal reflection artifacts and calculating system zero-points using reference comparison stars.
* `utils/history_tracker.py`: Scans the Seestar observation storage to update last_observed timestamps in the campaign database.
* `utils/inject_location.py`: Dynamically synchronizes Bridge/Simulator location using config.toml as the source of truth.
* `utils/inspect_comp.py`: Visual validation utility to safely inspect comparison star coordinates and chart structures.
* `utils/inspect_comp_deep.py`: Deep-dive diagnostic tool to inspect and preview raw JSON comparison star chart contents.
* `utils/manifest_auditor.py`: Audits target lists against comparison charts to link active targets with canonical AUIDs and coordinates.
* `utils/notifier.py`: Outbound notification manager that generates morning reports and sends mission summaries via Telegram.
* `utils/platesolve_analyst.py`: Quantitative reporter for plate-solving success rates, performing blind solves to compare header coordinates against reality.
* `utils/quick_phot.py`: Lightweight instrumental photometry script for rapid magnitude estimation and zero-point offset calculation.
* `utils/undo_header_mess.py`: Emergency recovery script to strip failed header automation attempts and restore file integrity.
* `utils/wvs_ingester.py`: Downloads and parses the KNVWS Werkgroep Veranderlijke Sterren program list to automate local campaign alignment.
* `core/utils/chrony_monitor.py`: No objective defined.
* `core/utils/disk_monitor.py`: Verifies NAS and local USB/buffer storage availability across all flight phases.
* `core/utils/gps_monitor.py`: Monitor GPSD natively via TCP socket (bypassing broken pip libraries),
* `core/utils/observer_math.py`: Calculate the 6-character Maidenhead Locator (e.g., JO22hj).
* `core/utils/sys_monitor.py`: No objective defined.
* `core/flight-to-post-handover.py`: Secures data after a mission, stops hardware bridges, and triggers post-flight analysis.
* `core/post_to_pre_feedback.py`: Updates targets.json with successful observation dates.
* `core/pre-to-flight-handover.py`: Evaluates final preflight vitals to authorize the transition to the FLIGHT phase or abort the mission if unsafe.
* `core/selector.py`: Prioritize targets setting in the West during the dark window.
* `core/sequence_repository.py`: Local cache manager for AAVSO V-band comparison sequences, reducing API overhead for offline planning.

