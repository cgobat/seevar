# 🚀 PREFLIGHT CHECKLIST

** Objective: Safety checks and environmental verification required before opening the dome.

## Phase 1: The Data Funnel
1. **state_flusher.py**: Resets `system_state.json` to IDLE.
2. **aavso_fetcher.py**: Hauls targets from AAVSO TargetTool.
3. **chart_fetcher.py**: Downloads 90' FOV photometry charts.
4. **librarian.py**: Cross-references targets against local chart cache.
5. **nightly_planner.py**: Filters by Haarlem physical horizon (30° floor).
6. **ledger_manager.py**: Applies the 3-day scientific cadence rule.
