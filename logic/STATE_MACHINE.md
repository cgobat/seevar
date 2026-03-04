# S30-PRO Federation: Finite State Machine (FSM) v1.0

## 1. Overview
This document defines the deterministic states of the Orchestrator. Every state change MUST be recorded atomically to `system_state.json`.

## 2. State Definitions

| State | Context | Valid Next States |
| :--- | :--- | :--- |
| **IDLE** | System is parked and awaiting `tonights_plan.json`. | EVALUATING |
| **EVALUATING** | Triage loop is running (Horizon/Solar/Priority checks). | QUEUED, FAILED |
| **QUEUED** | Target list is approved and ready for hardware. | SLEWING |
| **SLEWING** | Commands sent to Seestar mount to move to RA/Dec. | TRACKING, FAILED |
| **TRACKING** | Mount has reached target; Centering/Plate-solving. | INTEGRATING, FAILED |
| **INTEGRATING** | Active acquisition. FITS files are hitting the disk. | VERIFYING, FAILED |
| **VERIFYING** | Librarian is validating FITS header and SNR. | COMPLETED, FAILED |
| **PARKING** | End of session or Weather Veto triggered. | IDLE |

## 3. Terminal Outcomes (Ledger Status)
- **COMPLETED**: Target met full integration time and passed SNR audit.
- **SKIPPED**: Target vetoed by Triage (Solar/Horizon) or manual override.
- **FAILED**: Hardware error, Bridge timeout, or Weather interruption.

## 4. Recovery Logic
Upon restart, the Orchestrator reads `system_state.json`. If the state is not `IDLE` or `PARKED`, the system must attempt a `SAFE_RECOVERY` (Park mount) before resuming the Triage loop.
