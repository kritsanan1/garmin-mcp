# 🏃 Garmin MCP Server

**OpenClaw Platform · Port 8422**

FastMCP server for Garmin Connect — live GPS tracking, health metrics, and activity data for AI agents.

---

## ⚡ Quick Start

```bash
# 1. Clone / enter project
cd garmin-mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env → set GARMIN_EMAIL and GARMIN_PASSWORD

# 4. Run server
python server.py
```

Server starts at: `http://localhost:8422`

**First run** logs into Garmin Connect and caches the session token at `~/.garmin_mcp_tokens`.
Subsequent runs reuse the cached token (no re-login needed).

---

## 🛠️ Tools (12 total)

| # | Tool | Description |
|---|------|-------------|
| 1 | `garmin_get_daily_summary` | Steps, HR, stress, calories, sleep, distance |
| 2 | `garmin_get_heart_rate` | Resting/max HR + time-series timeline |
| 3 | `garmin_get_steps` | 15-min interval step breakdown |
| 4 | `garmin_get_sleep` | Deep/light/REM/awake stages + score |
| 5 | `garmin_get_stress` | Avg/max stress + ASCII chart |
| 6 | `garmin_get_body_battery` | Energy levels over 1–7 day range |
| 7 | `garmin_list_activities` | Recent activities with IDs for drill-down |
| 8 | `garmin_get_activity_details` | Full activity stats + lap splits |
| 9 | `garmin_get_gps_track` | GPS coordinates from recorded activity |
| 10 | `garmin_get_livetrack` | **Real-time** position via LiveTrack polling |
| 11 | `garmin_get_hrv` | HRV last-night + weekly average |
| 12 | `garmin_get_training_readiness` | Today's readiness score + factors |

---

## 📡 LiveTrack Real-time GPS

1. On your Garmin device → start activity → enable **LiveTrack**
2. Garmin sends a share URL to your contacts, e.g.:
   `https://livetrack.garmin.com/session/abc123.../token/xyz...`
3. Extract the **session token** (between `/session/` and `/token/`)
4. Call `garmin_get_livetrack` with that token — positions update ~every 4 seconds

---

## 🔌 OpenClaw Integration

Add to your OpenClaw config:

```yaml
skills:
  - name: garmin-health
    transport: streamable-http
    url: http://localhost:8422
```

Or connect via MCP protocol URL in Claude Desktop:
```
http://localhost:8422/sse
```

---

## 🔐 Auth Notes

- Uses the unofficial `garminconnect` Python library (no Garmin Developer Program approval needed)
- Tokens cached at `~/.garmin_mcp_tokens` — delete this file to force re-login
- Garmin may prompt for 2FA on first login in some regions
- Rate limiting: avoid calling more than ~100 times/hour to prevent IP blocks

---

## 📁 Project Structure

```
garmin-mcp/
├── server.py          # FastMCP server (12 tools)
├── garmin_client.py   # Auth + session wrapper
├── models.py          # Pydantic v2 input models
├── utils.py           # Markdown/JSON formatters
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🌐 Response Formats

All tools support `response_format`:
- `"markdown"` (default) — human-readable tables, great for chat UIs
- `"json"` — raw Garmin API data, great for downstream processing

---

*Built for the Dr. Arty+ Team · OpenClaw Platform · 2026*
