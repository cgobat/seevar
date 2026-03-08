# 🕰️ SEESTAR CADENCE LOGIC (Photometry Workflow)

> **Objective:** Ensure "Science-Grade" sampling of Variable Stars (LPVs/Miras/SRs) by adhering to AAVSO cadence requirements.

---

## 📐 1. THE SAMPLING RULE
To capture a scientifically valid light curve, the scheduler must sample at **1/20th of the target's period**.

| Variable Type | Period Range | Recommended Cadence | Logic Trigger |
| :--- | :--- | :--- | :--- |
| **Mira** | 200–500d | Every 5–10 days | $P / 20 \approx 10d$ |
| **Semi-Regular (SR)** | 100–200d | Every 3–5 days | $P / 20 \approx 5d$ |
| **Fast SR** | < 100d | Every 1–3 days | $P / 20 \approx 2d$ |

---

## 🔄 2. THE SCHEDULING WORKFLOW
The state machine iterates through `tonights_plan.json` using the following priority calculation:

1. **Last_Observed**: Retrieve timestamp from local logs/FITS header.
2. **Cadence_Delta**: Calculate `(Current_Time - Last_Observed)`.
3. **Priority_Score**:
    * If `Cadence_Delta >= Recommended_Cadence`, target is **CRITICAL**.
    * If `Cadence_Delta < Recommended_Cadence`, target is **DEFERRED**.
4. **Altitude Check**: Only execute if `tonight_alt` > 30° to minimize airmass extinction.

---

## 🛠️ 3. "SOVEREIGNTY" STATE INTEGRATION
For every target selected by the cadence logic, the hardware must follow the **Diamond Revision** sequence:

1. **Pre-Slew**: `iscope_stop_view` (Stage: AutoStack) to clear previous state.
2. **Navigation**: `scope_sync` using **Keyed Object Dialect** `{"ra": X, "dec": Y}`.
3. **Integration**: `start_exposure` (Single Frame Mode) for a minimum of 300s.
4. **Harvest**: Capture the RAW FITS via `get_last_image`.
