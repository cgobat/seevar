# 🧬 AAVSO LOGIC

** Objective: Rules for scientific targeting, cadence, and AAVSO report formatting.

# 🧬 AAVSO LOGIC

** Objective: Rules for scientific targeting, cadence, and AAVSO report formatting.

# 🧬 AAVSO LOGIC

** Objective: Rules for scientific targeting, cadence, and AAVSO report formatting.
# 🧬 AAVSO LOGIC & AUTHENTICATION

> **Objective**: Manage the handshake between Seestar data and AAVSO standards.
> **Version**: 1.3.0

## 🔗 VSP API Connection (External)
- **Canonical Host**: `apps.aavso.org`
- **Endpoint**: `/vsp/api/chart/`
- **Auth**: HTTP Basic (Username: `TARGET_KEY`, Password: `api_token`)

## 🔭 Photometry Requirements (S30-PRO)
- **Primary Channel**: Green (extract from RGGB Bayer for Johnson V approximation).
- **Sub-Exposures**: 30s - 60s single RAW frames (via `start_exposure`).
- **Reporting**: Data must be formatted to the AAVSO Extended Format (REDA).

## ⏳ Throttling (The "Pi-Sleep")
- **Mandatory Delay**: 31.4s between API calls to `apps.aavso.org` to avoid IP lockout.
