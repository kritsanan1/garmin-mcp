---
name: garmin-mcp
description: >
  Real-time Garmin Connect integration for AI agents. 12 FastMCP tools covering
  live GPS tracking (LiveTrack), heart rate, sleep stages, stress, body battery,
  steps, HRV, training readiness, and full activity history with GPS export.
  Runs as a local Python HTTP server on port 8422.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🏃"
    homepage: https://github.com/kritsanan1/garmin-mcp
    primaryEnv: GARMIN_EMAIL
    requires:
      env:
        - GARMIN_EMAIL
        - GARMIN_PASSWORD
      bins:
        - python3
    envVars:
      - name: GARMIN_EMAIL
        required: true
        description: Garmin Connect account email address.
      - name: GARMIN_PASSWORD
        required: true
        description: Garmin Connect account password.
      - name: GARMIN_TOKEN_STORE
        required: false
        description: Path to cached auth token file (default ~/.garmin_mcp_tokens).
      - name: GARMIN_MCP_PORT
        required: false
        description: HTTP port for the MCP server (default 8422).
    install:
      - kind: uv
        package: "mcp[cli]"
        bins: []
      - kind: uv
        package: garminconnect
        bins: []
      - kind: uv
        package: garth
        bins: []
      - kind: uv
        package: pydantic
        bins: []
      - kind: uv
        package: python-dotenv
        bins: []
      - kind: uv
        package: httpx
        bins: []
---

# 🏃 garmin-mcp

Real-time Garmin Connect integration for AI health and fitness agent workflows.
Exposes 12 FastMCP tools covering live GPS, all health metrics, and full
activity history. Runs as a persistent local HTTP MCP server on port **8422**.

## Setup

```bash
cp .env.example .env
# Set GARMIN_EMAIL and GARMIN_PASSWORD
pip install -r requirements.txt
./run.sh
```

Connect to OpenClaw:
```yaml
skills:
  - name: garmin-health
    transport: streamable-http
    url: http://localhost:8422
```

## Tools

| Tool | Description |
|------|-------------|
| `garmin_get_daily_summary` | Steps, HR, stress, calories, sleep, distance |
| `garmin_get_heart_rate` | Resting/max HR + time-series timeline |
| `garmin_get_steps` | 15-min interval step breakdown |
| `garmin_get_sleep` | Deep/light/REM/awake stages + score |
| `garmin_get_stress` | Avg/max stress + ASCII chart |
| `garmin_get_body_battery` | Energy levels over 1–7 day range |
| `garmin_list_activities` | Recent activities with IDs |
| `garmin_get_activity_details` | Full activity stats + lap splits |
| `garmin_get_gps_track` | GPS coordinates from recorded activity |
| `garmin_get_livetrack` | Real-time LiveTrack position |
| `garmin_get_hrv` | HRV last-night + weekly average |
| `garmin_get_training_readiness` | Readiness score 0-100 + coaching feedback |

All tools: `response_format="markdown"` (default) or `"json"`. Dates default to today.

## LiveTrack (Real-time GPS)
1. Start activity on Garmin device → enable LiveTrack
2. Extract token from share URL: `livetrack.garmin.com/session/{TOKEN}/token/...`
3. Call `garmin_get_livetrack(session_token=TOKEN)` — updates every ~4 seconds

## Notes
- Uses unofficial `garminconnect` library — no Garmin Developer Program approval needed
- Session cached at `~/.garmin_mcp_tokens` after first login
- Rate limit: ~100 calls/hour max
