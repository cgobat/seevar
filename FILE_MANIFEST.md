# Seestar Organizer File Manifest

| Path | Version | Objective |
| :--- | :--- | :--- |
| core/preflight/aavso_fetcher.py | 1.4.0 | Authenticated AAVSO VSP query using S30 FOV (168 arcmin) and mandatory maglimit. |
| core/preflight/audit.py | N/A | Enforces scientific cadence. Cross-references targets with ledger.json. |
| core/preflight/consolidator.py | 1.1.0 | Unified funnel with "Solar Veto" to scrub targets in conjunction. |
| core/preflight/disk_usage_monitor.py | 1.0.1 | Monitor S30 internal storage via SMB mount and update system state. |
| core/preflight/fog_monitor.py | 1.0.0 | Infrared sky-clarity monitor using MLX90614 to prevent imaging in fog. |
| core/preflight/gps.py | 1.0.0 | Manages geographic coordinates using config.toml as the source of truth. |
| core/preflight/hardware_audit.py | 1.1.0 | Comprehensive hardware audit including leveling, EQ mode status, and coordinate verification. |
| core/preflight/harvester.py | N/A | No objective defined. |
| core/preflight/horizon.py | 1.0.0 | Veto targets based on local obstructions (Trees, Buildings) using Az/Alt mapping. |
| core/preflight/librarian.py | 2.1.0 | Managed the AAVSO raw harvest and seeds the catalogs/ directory. |
| core/preflight/nightly_planner.py | 2.2.0 | Executes the 6-step filtering funnel with real-time Alt/Az visibility verification. |
| core/preflight/preflight_checklist.py | 1.0.0 | Verify bridge connectivity, mount orientation, and imaging pipeline status prior to flight. |
| core/preflight/seeing_scraper.py | N/A | No objective defined. |
| core/preflight/sync_location.py | 1.3.0 | Synchronize S30 location using the verified open Port 80. |
| core/preflight/target_evaluator.py | N/A | Audits the nightly plan for freshness and quantity. |
| core/preflight/weather.py | 2.0.2 | Tri-Source Emoticon Aggregator for astronomical weather prediction (Strictly Dynamic Coordinates). |
| core/flight/__init__.py | N/A | No objective defined. |
| core/flight/env_loader.py | N/A | Centralized configuration and environment variable manager. |
| core/flight/filesystem_control.py | 1.1.2 | Manage S30 Samba mount and harvest images to a dedicated /images folder. |
| core/flight/flight-to-post-handover.py | 1.2.0 | Secures data after a mission, stops hardware bridges, and triggers post-flight analysis workflows. |
| core/flight/hardware_profiles.py | N/A | Define sensor specs for Annie (S50), Williamina (S30-Pro), and Henrietta (S30-Pro Fast). |
| core/flight/mount_control.py | 1.4.3 | Secure mount orientation by parsing nested JSON-RPC responses from the Alpaca bridge. |
| core/flight/neutralizer.py | 2.4.0 | 3-finger salute, generous 180s deep sleep, ping for life, then verify Zero-State. |
| core/flight/orchestrator.py | 2.0.0 | Upload the mission JSON and trigger the state machine from a verified Zero-State. |
| core/flight/reboot.py | 1.1.0 | Issue a hard reboot to a Seestar, monitor network state, and verify API readiness. |
| core/flight/vault_manager.py | 1.2.0 | Manages secure access to observational metadata and synchronizes GPS coordinates with config.toml. |
| core/postflight/analyst.py | N/A | Analyzes FITS image quality, FWHM, and basic observational metrics. |
| core/postflight/analyzer.py | N/A | Validates FITS headers and calculates basic QC metrics. |
| core/postflight/aperture_photometry.py | 1.0.0 | Extract instrumental flux and magnitude using aperture photometry on precise WCS coordinates. |
| core/postflight/calibration_engine.py | N/A | Manages Zero-Point (ZP) offsets and flat-field corrections for the IMX585. |
| core/postflight/differential_photometry.py | 1.0.0 | Perform differential aperture photometry using a target and a known comparison star. |
| core/postflight/ensemble_photometry.py | 1.1.0 | Ensemble photometry using verified AAVSO coordinates and magnitudes for Algol. |
| core/postflight/fits_auditor.py | 1.3.0 | Scrapes full AAVSO-relevant keyword set for scientific submission. |
| core/postflight/fits_harvester.py | 1.1.0 | Transfer raw FITS from Seestar's internal 'MyWorks' to the Pi's physical USB vault. |
| core/postflight/fits_inspector.py | 1.0.0 | Perform forensics on unknown FITS files to determine sensor size and residual headers. |
| core/postflight/knvws_reporter.py | N/A | No objective defined. |
| core/postflight/master_analyst.py | N/A | High-level plate-solving coordinator for narrow-field Seestar frames. |
| core/postflight/notifier.py | N/A | Outbound alert management via Telegram and system bells. |
| core/postflight/pastinakel_math.py | N/A | Logic for saturation detection and dynamic aperture scaling. |
| core/postflight/photometry_engine.py | N/A | Instrumental flux extraction and science-grade lightcurve generation. |
| core/postflight/photometry_targeter.py | 1.0.0 | Use WCS headers to translate celestial RA/Dec into exact X/Y image pixels. |
| core/postflight/pixel_mapper.py | N/A | Converts celestial WCS coordinates to local sensor pixel X/Y coordinates. |
| core/postflight/post_to_pre_feedback.py | 1.2.0 | Updates the master targets.json with successful observation dates extracted from QC reports. |
| core/postflight/sync_manager.py | N/A | Manages file synchronization between Seestar, Local Buffer, and NAS. |
| logic/dictionary_harvester.py | 1.0.0 | Execute all commands in seestar_dict.psv and record the actual S30 responses. |
| logic/scout.py | 1.2.0 | Crawl local Bruno collection to extract commands and payloads for the PSV dictionary using absolute paths. |
| logic/seestar_dict.psv | N/A | No objective defined. |
| logic/test_r_leo.py | N/A | No objective defined. |
| tests/alpaca_simulator.py | 1.0.0 | Mock Alpaca bridge to simulate Seestar hardware responses and state transitions for safe indoor logic testing. |
| tests/monitor_mission.py | 1.0.0 | Parse the SSC schedule feedback and Alpaca telemetry to verify mission execution. |
| tests/park_mount.py | 1.0.0 | Safely fold the physical mount, disengage tracking, and disconnect the Alpaca bridge. |
| tests/test_slew.py | 1.2.0 | Execute Alpaca sequence with explicit UNPARK command to bypass hardware safety locks. |
| tests/test_sun.py | 1.0.0 | Execute a direct daytime Alpaca slew to the Sun's exact coordinates for March 6, 2026. |
| tests/test_sync_haarlem.py | 1.0.0 | Synchronize S30 location (Haarlem) via Port 5555 Alpaca using PSV vocabulary. |
| tests/test_vitals_polling.py | 1.5.0 | Use the absolute PSV strings to poll the S30 via Port 5555. |
| utils/aavso_client.py | 1.2.0 | Low-level API client for authenticated AAVSO VSX and WebObs data retrieval. |
| utils/astro.py | 1.2.0 | Core library for RA/Dec parsing, sidereal time, and coordinate math. |
| utils/audit_setup.py | 1.2.0 | Dumps current Horizon and Target configuration for architectural review. |
| utils/auto_header.py | 1.2.0 | Injects standardized file headers into Python scripts across the project. |
| utils/bridge_probe.py | N/A | No objective defined. |
| utils/campaign_auditor.py | 1.2.0 | Unpacks the JSON envelope and cross-references campaign targets with available AAVSO comparison charts via coordinates. |
| utils/campaign_cleaner.py | 1.2.0 | Deduplicates root campaign targets and securely links them via robust coordinate parsing. |
| utils/cleanup.py | 1.2.0 | Housekeeping utility for purging temporary files and rotating stale logs to prevent storage bloat. |
| utils/comp_purger.py | 1.2.0 | Scans comparison charts and deletes any file that is empty, malformed, or missing coordinate data. |
| utils/coordinate_converter.py | 1.2.0 | Ensures data validity by converting sexagesimal AAVSO coordinates into decimal degrees for internal computational use and plate-solving. |
| utils/dictionary_harvester.py | 2.0.0 | Execute commands in seestar_dict.psv via the pure Alpaca REST API and record JSON responses. |
| utils/factory_rebuild.py | N/A | No objective defined. |
| utils/fix_imports.py | 1.2.0 | Automated namespace correction utility for project-wide absolute import resolution. |
| utils/generate_manifest.py | 1.1.2 | Generate a comprehensive FILE_MANIFEST.md from the utils/ directory. |
| utils/history_tracker.py | 1.2.0 | Scans the Seestar observation storage to update last_observed timestamps in the campaign database. |
| utils/init_ledger.py | 1.5.3 | Initializes the master Ledger with proper headers and PENDING status. |
| utils/inject_location.py | 1.2.0 | Dynamically synchronizes Bridge/Simulator location using config.toml as the source of truth. |
| utils/manifest_auditor.py | 1.2.0 | Audits target lists against comparison charts to link active targets with canonical AUIDs and coordinates. |
| utils/migrate_schema.py | N/A | No objective defined. |
| utils/notifier.py | 1.2.0 | Outbound notification manager that generates morning reports and sends mission summaries via Telegram. |
| utils/platesolve_analyst.py | 1.2.0 | Quantitative reporter for plate-solving success rates, performing blind solves to compare header coordinates against reality. |
| utils/purify_catalog.py | 1.1.0 | Wraps the raw 409-target list into a Federation-standard JSON with metadata. |
| utils/quick_phot.py | 1.2.0 | Lightweight instrumental photometry script for rapid magnitude estimation and zero-point offset calculation. |
| utils/setup_wizard.py | 1.5.2 | Automates hardware discovery using the alpacadiscovery1 handshake. |
| utils/test_coords.py | N/A | Verifies target acquisition readiness for existing decimal coordinates. |
| utils/wvs_ingester.py | 1.2.0 | Downloads and parses the KNVWS Werkgroep Veranderlijke Sterren program list to automate local campaign alignment. |
