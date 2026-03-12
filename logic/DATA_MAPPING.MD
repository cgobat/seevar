# 🧠 S30-PRO Data Lifecycle

> **Objective:** Tracking data from AAVSO fetch to FITS acquisition.
> **Version:** 1.4.0

1. **RAW FETCH**: `sync_catalog.py` pulls from AAVSO -> `targets.json`.
2. **ENRICHMENT**: `fetch_sequences.py` hits VSP API for comp-stars -> `sequences/*.json`.
3. **REFINEMENT**: `nightly_planner.py` applies GPS/Horizon math -> `tonights_plan.json`.
4. **EXECUTION**: `session_manager.py` utilizes the `start_exposure` loop.
5. **ACQUISITION**: `get_stacked_img` pulls FITS to `local_buffer/`.
