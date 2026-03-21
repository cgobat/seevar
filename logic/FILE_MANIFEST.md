# 🔭 SeeVar: File Manifest

> **System State**: Diamond Revision (Sovereign)

| Path | Version | Objective |
| :--- | :--- | :--- |
| requirements.txt | 2026.03.18 | SeeVar runtime dependencies — delta on top of seestar_alp. |
| config.toml | N/A | No objective defined. |
| core/fed-mission | 2.6.1 | Full cycle automation including Postflight FITS Verification. |
| core/federation-dashboard.service | N/A | No objective defined. |
| core/ledger_manager.py | 1.6.1 | The High-Authority Mission Brain. Manages target cadence and observation history. Filters tonights_plan.json by cadence, records attempts and successes during flight. |
| core/seeing-scraper.service | N/A | No objective defined. |
| core/seeing-scraper.timer | N/A | No objective defined. |
| core/seestar_env_lock.service | N/A | No objective defined. |
| core/hardware/fleet_mapper.py | 2.0.0 | Read [[seestars]] from config.toml, load hardware constants |
| core/hardware/hardware_loader.py | 1.2.0 | Auto-detect Seestar hardware via Alpaca UDP discovery beacon (port 32227), fingerprint sensor via HTTP Alpaca API, load the matching hardware profile. |
| core/hardware/ladies.txt | N/A | No objective defined. |
| core/hardware/ssh_monitor.py | 1.1.0 | Establish an SSH connection to the Seestar SOC (ARM) to stream real-time logs for reverse-engineering port 4700 Sovereign commands. Includes an interactive menu for log selection. |
| core/hardware/models/S30-Pro.json | JSON | Data/Configuration file. |
| core/hardware/models/S30.json | JSON | Data/Configuration file. |
| core/hardware/models/S50.json | JSON | Data/Configuration file. |
| core/postflight/aavso_reporter.py | 1.2.1 | Generate AAVSO Extended Format reports in the dedicated data/reports/ |
| core/postflight/accountant.py | 2.0.1 | Sweeps local_buffer, runs full Bayer differential photometry via calibration_engine, and stamps complete results into the ledger. |
| core/postflight/bayer_photometry.py | 2.0.1 | Bayer-channel aperture photometry engine for the IMX585 (GRBG pattern). Extracted from pilot.py and elevated to a standalone science module. Provides single-star flux extraction and multi-star differential photometry. |
| core/postflight/calibration_engine.py | 2.0.0 | Orchestrates differential photometry for a single FITS frame. |
| core/postflight/gaia_resolver.py | 1.0.0 | Resolve Gaia DR3 comparison stars for a given field. |
| core/postflight/librarian.py | 2.2.1 | Securely harvest binary FITS to RAID1; prepare for NAS archival using dynamic paths. |
| core/postflight/master_analyst.py | 2.0.1 | High-level plate-solving coordinator executing astrometry.net's solve-field. |
| core/postflight/pastinakel_math.py | 1.1.2 | Logic for saturation detection and dynamic aperture scaling. |
| core/postflight/post_to_pre_feedback.py | 1.2.2 | Updates the master targets.json with successful observation dates extracted from QC reports. |
| core/postflight/psf_models.py | 1.0.1 | PSF fitting for stellar profiles on IMX585 Bayer frames. Provides FWHM estimation feeding dynamic aperture and SNR calculations. |
| core/postflight/data/qc_report.json | JSON | Data/Configuration file. |
| core/flight/camera_control.py | 2.0.0 | Hardware status interface for ZWO S30-Pro via Sovereign TCP. |
| core/flight/dark_library.py | 1.0.0 | Post-session dark frame acquisition via firmware start_create_dark. |
| core/flight/exposure_planner.py | 1.2.0 | Estimate optimal exposure time and frame count for a target given |
| core/flight/field_rotation.py | 1.0.0 | Calculate field rotation rate and maximum safe exposure time for |
| core/flight/fsm.py | 1.0.0 | The Finite State Machine governing S30-PRO Sovereign Operations. |
| core/flight/mission_chronicle.py | 4.2.0 | Orchestrates the Preflight Funnel (Janitor -> Librarian -> Auditor -> Planner). |
| core/flight/neutralizer.py | 3.0.1 | Hardware reset — stops any active S30-Pro session and verifies idle state before handing control to the pilot. |
| core/flight/orchestrator.py | 1.6.1 | Full pipeline state machine wired to the TCP Diamond Sequence. M4: DarkLibrary wired into post-session flow. |
| core/flight/pilot.py | 1.6.2 | Direct TCP control of ZWO S30-Pro for AAVSO-compliant Sovereign RAW acquisition. Dynamically routes network IP from config. |
| core/flight/sim_runner.py | 1.0.0 | Execute a full realtime nightly simulation against tonights_plan.json |
| core/flight/vault_manager.py | 1.4.1 | Secure metadata access with actual bi-directional tomli_w syncing. |
| core/dashboard/dashboard.py | 4.5.3 | Remove hardcoded local coordinates; fallback to Greenwich. |
| core/dashboard/templates/index.html | N/A | No objective defined. |
| core/preflight/aavso_fetcher.py | 1.6.1 | Step 1 - Haul scientific targets from AAVSO Target Tool API and append strict CADENCE.md sampling rules. |
| core/preflight/audit.py | 1.4.0 | Enforces scientific cadence (1/20th rule) by properly parsing ledger dictionaries. |
| core/preflight/chart_fetcher.py | 1.4.2 | Step 2 - Fetch AAVSO VSP comparison star sequences. |
| core/preflight/disk_monitor.py | 1.1.2 | Verifies storage availability. Respects location context: NAS is only audited when on the Home Grid. |
| core/preflight/disk_usage_monitor.py | 1.1.1 | Monitor S30 internal storage via SMB mount and update system state with Go/No-Go veto. |
| core/preflight/fog_monitor.py | 1.0.1 | Infrared sky-clarity monitor using MLX90614 to prevent imaging in fog. Acts as a safety gate for photometry. |
| core/preflight/gps.py | 1.5.1 | Bi-directional GPS provider with lazy initialization. Reads from RAM status and actively syncs to config.toml via VaultManager to maintain a live last_refresh heartbeat. |
| core/preflight/hardware_audit.py | 2.0.0 | Sovereign TCP hardware audit via get_device_state on port 4700. |
| core/preflight/horizon.py | 2.0.0 | Veto targets based on local obstructions using Az/Alt mapping. |
| core/preflight/ledger_manager.py | 2.2.1 | The High-Authority Mission Brain. Manages dynamic target cadence |
| core/preflight/librarian.py | 4.3.0 | The Single Source of Truth. Parses raw AAVSO haul, checks for VSP charts, and writes the Federation Catalog. |
| core/preflight/nightly_planner.py | 2.6.1 | Filters the audited Federation Catalog by Cadence, Horizon, and Altitude (Unified Config). |
| core/preflight/preflight_checklist.py | 2.0.0 | Sovereign preflight gate — verifies hardware is alive and at |
| core/preflight/schedule_compiler.py | 1.0.1 | Translates tonights_plan.json into a native SSC JSON payload using the 1x1 mosaic hack for dithering. |
| core/preflight/state_flusher.py | 1.1.1 | Preflight utility to flush stale system state and reset the dashboard to IDLE before a new flight. |
| core/preflight/target_evaluator.py | 1.0.2 | Audits the nightly plan for freshness and quantity to update dashboard UI. |
| core/preflight/vsx_catalog.py | 2.0.1 | Fetch magnitude ranges from AAVSO VSX for all campaign targets. |
| core/preflight/weather.py | 1.8.0 | Tri-source weather consensus daemon. Evaluates hard-abort |
| core/utils/aavso_client.py | 1.2.2 | Low-level API client for authenticated AAVSO VSX and WebObs data retrieval. Returns JSON-ready dictionaries with #objective tags. |
| core/utils/astro.py | 1.2.1 | Core library for RA/Dec parsing, sidereal time, and coordinate math. |
| core/utils/coordinate_converter.py | 1.2.2 | Ensures data validity by converting sexagesimal AAVSO coordinates into decimal degrees, appending #objective to JSON writes. |
| core/utils/env_loader.py | 1.1.0 | Single source of truth for SeeVar environment paths and TOML configuration loading. |
| core/utils/gps_monitor.py | 1.5.0 | Continuous native GPSD socket monitor with full resource safety, |
| core/utils/notifier.py | 1.4.0 | Outbound alert management via Telegram and system bell. |
| core/utils/observer_math.py | 1.0.3 | Mathematical utilities for observational astronomy, including Maidenhead grid calculations dynamically tested against config.toml. |
| core/utils/platesolve_analyst.py | 1.2.2 | Quantitative reporter for plate-solving success rates, performing blind solves to compare header coordinates against reality. |
| logic/FILE_MANIFEST.md | N/A | No objective defined. |
| dev/CONTRIBUTING.md | N/A | ** Defines the strict technical standards, workflow protocols, and "Garmt" purified header requirements for all project contributors (AI or Human). |
| dev/media/texts/03c6342ed25e222e.svg | N/A | No objective defined. |
| dev/media/texts/08cc01905f988ff0.svg | N/A | No objective defined. |
| dev/media/texts/0956741573e43ad2.svg | N/A | No objective defined. |
| dev/media/texts/0b07091eea0bd6ab.svg | N/A | No objective defined. |
| dev/media/texts/165880895d0a0e9c.svg | N/A | No objective defined. |
| dev/media/texts/1de1098a6301b302.svg | N/A | No objective defined. |
| dev/media/texts/209368ebfd3c402f.svg | N/A | No objective defined. |
| dev/media/texts/2243b5ae4f4f3027.svg | N/A | No objective defined. |
| dev/media/texts/29bfdc7e448e8b15.svg | N/A | No objective defined. |
| dev/media/texts/2bd04c716c7ceaf4.svg | N/A | No objective defined. |
| dev/media/texts/2c2165346f630775.svg | N/A | No objective defined. |
| dev/media/texts/3a99b8420aec1601.svg | N/A | No objective defined. |
| dev/media/texts/3d40d4b5e17be3a6.svg | N/A | No objective defined. |
| dev/media/texts/3e2335585fda2a36.svg | N/A | No objective defined. |
| dev/media/texts/43849ea3fc223e3c.svg | N/A | No objective defined. |
| dev/media/texts/490958af762e2e98.svg | N/A | No objective defined. |
| dev/media/texts/493bc3a4dd70e0a0.svg | N/A | No objective defined. |
| dev/media/texts/4b538ff50faef284.svg | N/A | No objective defined. |
| dev/media/texts/4cc8db7c2f318ad9.svg | N/A | No objective defined. |
| dev/media/texts/4ed40c8668d0f9dc.svg | N/A | No objective defined. |
| dev/media/texts/52456a1ac81779a6.svg | N/A | No objective defined. |
| dev/media/texts/5387a5cc6a0b71e9.svg | N/A | No objective defined. |
| dev/media/texts/560c2cbbd1ceb113.svg | N/A | No objective defined. |
| dev/media/texts/5b3fe7e03ea51757.svg | N/A | No objective defined. |
| dev/media/texts/605ba813867a1d37.svg | N/A | No objective defined. |
| dev/media/texts/69a2aff678b170be.svg | N/A | No objective defined. |
| dev/media/texts/6a23d8ae71a87249.svg | N/A | No objective defined. |
| dev/media/texts/6d87f38e40178cc6.svg | N/A | No objective defined. |
| dev/media/texts/73498860ed1fb247.svg | N/A | No objective defined. |
| dev/media/texts/7c13f4c5790437f2.svg | N/A | No objective defined. |
| dev/media/texts/83446f1adbe217c8.svg | N/A | No objective defined. |
| dev/media/texts/84484bbad0e4d7f9.svg | N/A | No objective defined. |
| dev/media/texts/84ecb6507e1797c7.svg | N/A | No objective defined. |
| dev/media/texts/865fadb6c0242b2d.svg | N/A | No objective defined. |
| dev/media/texts/920e9a8ad8960a14.svg | N/A | No objective defined. |
| dev/media/texts/9e5523507db5956b.svg | N/A | No objective defined. |
| dev/media/texts/a222f712f6687b83.svg | N/A | No objective defined. |
| dev/media/texts/a2ded987e6dbfbbf.svg | N/A | No objective defined. |
| dev/media/texts/a62ba7c50ef200f7.svg | N/A | No objective defined. |
| dev/media/texts/a73998e420d9d4e1.svg | N/A | No objective defined. |
| dev/media/texts/ab7a81acff1ac24f.svg | N/A | No objective defined. |
| dev/media/texts/ac29ded9e7d396e1.svg | N/A | No objective defined. |
| dev/media/texts/acda5dc3283c3f62.svg | N/A | No objective defined. |
| dev/media/texts/af8d40ec7eda1abb.svg | N/A | No objective defined. |
| dev/media/texts/b389f40cd2023845.svg | N/A | No objective defined. |
| dev/media/texts/b3f35b9e9eef0cb8.svg | N/A | No objective defined. |
| dev/media/texts/b6b5feb4f2cd7180.svg | N/A | No objective defined. |
| dev/media/texts/bd232d36268aa823.svg | N/A | No objective defined. |
| dev/media/texts/be7d4bff543e3913.svg | N/A | No objective defined. |
| dev/media/texts/c46996682172e503.svg | N/A | No objective defined. |
| dev/media/texts/c8baec18836c70d7.svg | N/A | No objective defined. |
| dev/media/texts/ca61ed68060d1097.svg | N/A | No objective defined. |
| dev/media/texts/cefc6a4ae815b81e.svg | N/A | No objective defined. |
| dev/media/texts/d99f6f370df24328.svg | N/A | No objective defined. |
| dev/media/texts/d9b21afd7572b603.svg | N/A | No objective defined. |
| dev/media/texts/d9b30271b292a12d.svg | N/A | No objective defined. |
| dev/media/texts/e0486fa369f089fb.svg | N/A | No objective defined. |
| dev/media/texts/e216ac72f8e10967.svg | N/A | No objective defined. |
| dev/media/texts/e31c1c00243568dd.svg | N/A | No objective defined. |
| dev/media/texts/e6a4d9b8b5a07c8d.svg | N/A | No objective defined. |
| dev/media/texts/eac2692179de2b9e.svg | N/A | No objective defined. |
| dev/media/texts/ef6046130bb81e4f.svg | N/A | No objective defined. |
| dev/media/texts/f3d301b3fc7a80e9.svg | N/A | No objective defined. |
| dev/media/texts/f576c40affafabe5.svg | N/A | No objective defined. |
| dev/media/texts/f8571154b9165b9a.svg | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/SovereignCommunicationFlow.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1051975923_3261201901.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1072645443_367394086.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1092915321_628548787.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1114850499_3782427124.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1162445995_1008864373.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1185031666_3946338301.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1202882417_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1202900741_585405432.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1219081991_3526852333.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1269170733_1083772885.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1269170733_560106470.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1271761585_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1276908948_2946656924.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1292664407_2565489991.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1318048752_1077468049.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1394669307_585405432.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1397656605_1367478698.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1455413721_3946338301.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1475160710_1028796893.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1493907286_3829485693.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1517789113_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1563029037_2309188324.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1563029037_3852739407.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1563518361_2919945446.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1563518361_927036454.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_158412184_1730363489.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1662707310_2946656924.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_171679747_3526852333.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1720989797_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1734327179_1939050573.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1775749707_1250615449.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1839128356_2674346697.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1858499479_2309188324.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1858499479_3852739407.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1868453191_2451470644.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1868453191_2626992711.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1868453191_2809237971.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1868453191_492172113.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1918140024_1250615449.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_1998252938_1008864373.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2050425811_1730363489.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2082040436_2026230769.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2184146037_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2248202233_262370941.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2324389150_628548787.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2391708859_493067453.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2408300941_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2601088877_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2636640538_3141087796.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2758018844_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2801759089_10939123.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_282690695_101755798.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_282690695_1476133041.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2946061346_3276895176.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_2954865941_3141087796.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_296110194_3829485693.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3046897085_101755798.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3046897085_1476133041.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3106401230_3500103713.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3203495204_3261201901.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3302620781_1229895896.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3332990854_262370941.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3354083468_626133876.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3638940092_1560746180.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3650934430_2919945446.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3650934430_927036454.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3683684618_3341307965.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3736542438_626133876.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3756453672_493067453.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3801323718_10939123.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3860300406_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3897537901_1229895896.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_3925337046_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_4064104827_3973560417.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_4095561764_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_472273494_3889047640.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_531025806_3089248537.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_555673935_3276895176.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_565174672_3013336365.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_597033972_367394086.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_633926470_1367478698.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_695175680_2167884204.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_801652120_473074668.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_801652120_812804464.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_805049217_2167884204.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_805049217_3013336365.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_805681882_1560746180.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_839518833_2451470644.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_839518833_2626992711.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_839518833_2809237971.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_839518833_492172113.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_843090367_473074668.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_843090367_812804464.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_936786336_3500103713.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_954547748_3576050009.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_965906468_1255159608.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_966603035_1083772885.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_966603035_560106470.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_981750519_3576050009.mp4 | N/A | No objective defined. |
| dev/media/videos/sovereign_flow/1080p60/partial_movie_files/SovereignCommunicationFlow/2135761390_99974539_1077468049.mp4 | N/A | No objective defined. |
| dev/tools/Kaspar.mp4 | N/A | No objective defined. |
| dev/tools/SeeVar_The_Movie.mp4 | N/A | No objective defined. |
| dev/tools/aavso_reporter_test.py | 1.0.0 | Generate a small dummy AAVSO Extended Format report for WebObs |
| dev/tools/build_trailer.sh | 1.0.2 | Robustly normalize and concatenate all SeeVar movie phases. |
| dev/tools/dummy_seestar_server.py | 1.0.0 | Local TCP server simulating the Seestar port 4700 JSON-RPC API for client testing. |
| dev/tools/edfilx.mp4 | N/A | No objective defined. |
| dev/tools/postflight_movie.py | 1.0.1 | Manim script visualizing the SeeVar Postflight pipeline: FITS ingestion, differential photometry, and AAVSO reporting. |
| dev/tools/rpc_client.py | 2.0.0 | Interactive JSON-RPC client for Seestar port 4700 using pre-built sovereign payloads. |
| dev/tools/seestar_jailbreak.py | 1.0.1 | Exploit Seestar OTA vulnerability on port 4350 to enable SSH and reset the root password. |
| dev/tools/sim_reset.py | 2.0.0 | Reset ledger entries for targets in tonights_plan.json to |
| dev/tools/sovereign_flow.py | 2.0.0 | Manim visualization of a 3-target JSON-RPC TCP sequence with an animated Seestar model and 12-second integration. |
| dev/tools/unpack_firmware.sh | 1.0.0 | Download the Seestar iOS application, extract the embedded firmware archive (zwo_iscope_update.tar.bz2), and unpack the Linux filesystem for static analysis. |
| dev/utils/comp_purger.py | 1.1.1 | Prunes orphaned comparison star charts in the SeeVar catalog. |
| dev/utils/generate_manifest.py | 1.5.2 | Generate FILE_MANIFEST.md for SeeVar and mirror it to NAS for quick reference. Ignores transient runtime data caches. |
| dev/utils/harvest_manager.py | 1.3.1 | SeeVar Harvester - Supports simulation data (.fit) and real FITS. |
| dev/utils/mount_guard.py | 1.1.1 | Check if the specified target is mounted and the required data directory exists. |
| dev/utils/nas_backup.sh | 1.3.2 | Backup SeeVar code and logic to dynamically defined NAS targets. |
| dev/logic/AAVSO_LOGIC.MD | N/A | ** Rules for scientific targeting, cadence, photometry |
| dev/logic/AI_CONTEXT.md | N/A | ** The absolute architectural law, environment standards, and logic constraints for AI-assisted development of the SeeVar Federation. |
| dev/logic/ALPACA_BRIDGE.MD | N/A | No objective defined. |
| dev/logic/API_PROTOCOL.MD | N/A | ** Definitive ZWO JSON-RPC method mapping for SeeVar. |
| dev/logic/ARCHITECTURE_OVERVIEW.md | N/A | ** High-precision AAVSO photometry via direct hardware control. |
| dev/logic/CADENCE.md | N/A | ** Ensure science-grade sampling of variable stars by |
| dev/logic/COMMUNICATION.md | N/A | No objective defined. |
| dev/logic/CORE.MD | N/A | ** Defines the chain of command and guiding principles for |
| dev/logic/DATALOGIC.MD | N/A | ** Defines the role, origin, and transformation logic for all JSON data structures within the RAID1 repository. |
| dev/logic/DATA_DICTIONARY.MD | N/A | ** Strict schema and ownership rules for every file in the |
| dev/logic/DATA_MAPPING.MD | N/A | ** Concise map of data flow from AAVSO fetch to FITS custody. |
| dev/logic/DISCOVERY_PROTOCOL.MD | N/A | UDP broadcast protocol for locating the Seestar S30 on the local network. |
| dev/logic/FILE_MANIFEST.md | N/A | No objective defined. |
| dev/logic/FLIGHT.MD | N/A | No objective defined. |
| dev/logic/PHOTOMETRICS.MD | N/A | No objective defined. |
| dev/logic/PICKERING_PROTOCOL.MD | N/A | No objective defined. |
| dev/logic/POSTFLIGHT.MD | N/A | No objective defined. |
| dev/logic/PREFLIGHT.MD | N/A | No objective defined. |
| dev/logic/README.MD | N/A | ** Definitive entry point and table of contents for the |
| dev/logic/README.md | N/A | ** Definitive entry point and table of contents for the foundational |
| dev/logic/SEEVAR_DICT.PSV | 2026.03 | No objective defined. |
| dev/logic/SIMULATORLOGIC.MD | N/A | No objective defined. |
| dev/logic/SIMULATORLOGIC.md | N/A | ** Outlines networking and state logic required to synchronize the SeeStar ALP Bridge with the Raspberry Pi Simulator environment. |
| dev/logic/STATE_MACHINE.md | N/A | ** Deterministic hardware transitions for sovereign AAVSO |
| dev/logic/WORKFLOW.md | N/A | No objective defined. |
| dev/logic/SEEVAR_SKILL/SKILL.md | N/A | No objective defined. |
| data/hardware_telemetry.json | JSON | Data/Configuration file. |
| data/horizon_mask.json | JSON | Data/Configuration file. |
| data/ledger.json | JSON | Data/Configuration file. |
| data/science_starlist.csv | N/A | No objective defined. |
| data/ssc_payload.json | JSON | Data/Configuration file. |
| data/system_state.json | JSON | Data/Configuration file. |
| data/tonights_plan.json | JSON | Data/Configuration file. |
| data/vsx_catalog.json | JSON | Data/Configuration file. |
| data/weather_state.json | JSON | Data/Configuration file. |
| systemd/seeing-scraper.service | N/A | No objective defined. |
| systemd/seeing-scraper.timer | N/A | No objective defined. |
| systemd/seestar_env_lock.service | N/A | No objective defined. |
| systemd/seevar-dashboard.service | N/A | No objective defined. |
| systemd/seevar-gps.service | N/A | No objective defined. |
| systemd/seevar-orchestrator.service | N/A | No objective defined. |
| systemd/seevar-weather.service | N/A | No objective defined. |
| catalogs/campaign_targets.json | JSON | Data/Configuration file. |
| catalogs/de421.bsp | N/A | No objective defined. |
| catalogs/federation_catalog.json | JSON | Data/Configuration file. |
