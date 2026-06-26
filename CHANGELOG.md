# Changelog

All notable changes to `garmin-mcp` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-06-26

### Added
- `garmin_get_daily_summary` — steps, HR, stress, body battery, calories, sleep, distance
- `garmin_get_heart_rate` — resting/max HR with time-series timeline
- `garmin_get_steps` — 15-minute interval step breakdown with activity classification
- `garmin_get_sleep` — deep/light/REM/awake stages + sleep score
- `garmin_get_stress` — average/max stress with ASCII bar chart timeline
- `garmin_get_body_battery` — energy levels over 1–7 day date range
- `garmin_list_activities` — recent activities table with IDs, type, distance, duration
- `garmin_get_activity_details` — full activity stats with optional lap splits
- `garmin_get_gps_track` — subsampled GPS coordinates from recorded activities
- `garmin_get_livetrack` — real-time GPS position polling via Garmin LiveTrack
- `garmin_get_hrv` — HRV last-night + weekly average + status
- `garmin_get_training_readiness` — readiness score 0–100 with coaching feedback
- Session token caching at `~/.garmin_mcp_tokens` — avoids re-login on restart
- `markdown` / `json` dual output format on all 12 tools
- `run.sh` with Python version check, auto-dependency install, and env validation
- Full Pydantic v2 input validation with range guards on all tools
- FastMCP HTTP transport on port 8422 (OpenClaw convention)
