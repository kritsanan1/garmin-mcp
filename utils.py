"""
utils.py
Response formatting helpers for Garmin MCP tools.
"""

import json
from datetime import datetime
from typing import Any, Optional


def to_json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def fmt_date(iso: Optional[str]) -> str:
    if not iso:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


def safe_get(d: dict, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d


def secs_to_hms(seconds: Optional[float]) -> str:
    if seconds is None:
        return "N/A"
    h, m, s = int(seconds) // 3600, (int(seconds) % 3600) // 60, int(seconds) % 60
    return f"{h}h {m:02d}m {s:02d}s" if h else f"{m}m {s:02d}s"


def meters_to_km(meters: Optional[float]) -> str:
    if meters is None:
        return "N/A"
    return f"{meters / 1000:.2f} km"


def fmt_daily_summary(data: dict, date: str) -> str:
    d = data or {}
    steps = d.get("totalSteps") or d.get("steps", 0)
    step_goal = d.get("dailyStepGoal") or d.get("stepGoal", 10000)
    calories = d.get("totalKilocalories") or d.get("activeKilocalories", 0)
    active_mins = d.get("highlyActiveSeconds", 0) // 60 + d.get("activeSeconds", 0) // 60
    distance = meters_to_km(d.get("totalDistanceMeters"))
    rest_hr = d.get("restingHeartRate")
    avg_stress = d.get("averageStressLevel", -1)
    body_battery_max = d.get("maxBodyBattery")
    body_battery_min = d.get("minBodyBattery")
    sleep_seconds = d.get("sleepingSeconds", 0)
    floors = d.get("floorsAscended", 0)
    stress_str = f"{avg_stress}" if avg_stress and avg_stress >= 0 else "N/A"
    bb_str = f"{body_battery_max} -> {body_battery_min}" if body_battery_max is not None else "N/A"
    return f"""# Daily Summary - {date}

| Metric          | Value                     |
|-----------------|---------------------------|
| Steps           | {steps:,} / {step_goal:,} |
| Distance        | {distance}                |
| Calories        | {calories:,} kcal         |
| Active Time     | {active_mins} min         |
| Floors          | {floors}                  |
| Resting HR      | {rest_hr or "N/A"} bpm    |
| Avg Stress      | {stress_str} / 100        |
| Body Battery    | {bb_str}                  |
| Sleep           | {secs_to_hms(sleep_seconds)} |

> Step progress: {round(steps / step_goal * 100) if step_goal else 0}%
"""


def fmt_heart_rate(data: dict, date: str) -> str:
    hr = data or {}
    resting = hr.get("restingHeartRate")
    max_hr = hr.get("maxHeartRate")
    min_hr = hr.get("minHeartRate")
    values = hr.get("heartRateValues") or []
    sample_count = len(values)
    timeline = ""
    if values:
        step = max(1, sample_count // 10)
        timeline = f"
**Samples (every ~{step} readings):**
"
        for ts, bpm in values[::step]:
            if bpm:
                t = datetime.fromtimestamp(ts / 1000).strftime("%H:%M")
                timeline += f"- {t} -> {bpm} bpm
"
    return f"""# Heart Rate - {date}

| Metric      | Value                   |
|-------------|-------------------------|
| Resting HR  | {resting or "N/A"} bpm  |
| Max HR      | {max_hr or "N/A"} bpm   |
| Min HR      | {min_hr or "N/A"} bpm   |
| Data Points | {sample_count}          |
{timeline}"""


def fmt_steps(data: list, date: str) -> str:
    if not data:
        return f"# Steps - {date}

No step data available."
    total = sum(d.get("steps", 0) for d in data if d.get("steps"))
    lines = [f"# Steps - {date}

**Total: {total:,} steps**

**Breakdown:**"]
    for item in data:
        start = item.get("startGMT", "")[:16]
        steps = item.get("steps", 0)
        ptype = item.get("primaryActivityLevel", "")
        if steps:
            lines.append(f"- {start}: {steps:,} steps ({ptype})")
    return "
".join(lines)


def fmt_sleep(data: dict, date: str) -> str:
    s = data.get("dailySleepDTO") or data or {}
    start = fmt_date(s.get("sleepStartTimestampGMT") or s.get("sleepStartTimestampLocal"))
    end = fmt_date(s.get("sleepEndTimestampGMT") or s.get("sleepEndTimestampLocal"))
    duration = secs_to_hms(s.get("sleepTimeSeconds"))
    deep = secs_to_hms(s.get("deepSleepSeconds"))
    light = secs_to_hms(s.get("lightSleepSeconds"))
    rem = secs_to_hms(s.get("remSleepSeconds"))
    awake = secs_to_hms(s.get("awakeSleepSeconds"))
    score = s.get("sleepScores", {}).get("overall", {}).get("value") if isinstance(s.get("sleepScores"), dict) else None
    return f"""# Sleep - {date}

| Stage   | Duration   |
|---------|------------|
| Total   | {duration} |
| Deep    | {deep}     |
| Light   | {light}    |
| REM     | {rem}      |
| Awake   | {awake}    |

**Bedtime:** {start}  **Wake up:** {end}  **Sleep Score:** {score or "N/A"}
"""


def fmt_stress(data: dict, date: str) -> str:
    s = data or {}
    avg = s.get("avgStressLevel", -1)
    max_stress = s.get("maxStressLevel", -1)
    stress_values = s.get("stressValuesArray") or []
    level_str = "N/A" if avg < 0 else str(avg)
    max_str = "N/A" if max_stress < 0 else str(max_stress)
    timeline = ""
    if stress_values:
        step = max(1, len(stress_values) // 8)
        timeline = "
**Stress Timeline:**
"
        for entry in stress_values[::step]:
            if isinstance(entry, list) and len(entry) >= 2 and entry[1] >= 0:
                t = datetime.fromtimestamp(entry[0] / 1000).strftime("%H:%M")
                bar = "#" * (entry[1] // 10) + "." * (10 - entry[1] // 10)
                timeline += f"- {t}: [{bar}] {entry[1]}
"
    return f"""# Stress - {date}

| Metric         | Value             |
|----------------|-------------------|
| Average Stress | {level_str} / 100 |
| Max Stress     | {max_str} / 100   |
| Data Points    | {len(stress_values)} |

> 0-25 = Resting | 26-50 = Low | 51-75 = Medium | 76-100 = High
{timeline}"""


def fmt_body_battery(data: list) -> str:
    if not data:
        return "# Body Battery

No data available."
    lines = ["# Body Battery
"]
    for entry in data:
        dt = entry.get("date", "")
        charged = entry.get("charged")
        drained = entry.get("drained")
        bb_values = entry.get("bodyBatteryValuesArray") or []
        current = bb_values[-1][1] if bb_values else "N/A"
        lines.append(f"**{dt}** - Current: {current} | Charged: {charged} | Drained: {drained}")
    return "
".join(lines)


def fmt_activities(data: list) -> str:
    if not data:
        return "# Activities

No activities found."
    lines = ["# Recent Activities
", "| ID | Type | Date | Duration | Distance |",
             "|----|------|------|----------|----------|"]
    for a in data:
        aid = a.get("activityId", "")
        atype = a.get("activityType", {}).get("typeKey", "") if isinstance(a.get("activityType"), dict) else a.get("activityType", "")
        date = (a.get("startTimeLocal") or a.get("startTimeGMT") or "")[:16]
        dur = secs_to_hms(a.get("duration") or a.get("elapsedDuration"))
        dist = meters_to_km(a.get("distance"))
        lines.append(f"| {aid} | {atype} | {date} | {dur} | {dist} |")
    return "
".join(lines)


def fmt_activity_details(activity: dict, splits: list) -> str:
    a = activity or {}
    name = a.get("activityName", "Activity")
    atype = safe_get(a, "activityType", "typeKey") or ""
    date = (a.get("startTimeLocal") or "")[:16]
    dur = secs_to_hms(a.get("duration"))
    dist = meters_to_km(a.get("distance"))
    avg_hr = a.get("averageHR")
    max_hr = a.get("maxHR")
    calories = a.get("calories")
    elevation = a.get("elevationGain")
    lines = [f"""# {name}

**Type:** {atype}  **Date:** {date}

| Metric    | Value                         |
|-----------|-------------------------------|
| Duration  | {dur}                         |
| Distance  | {dist}                        |
| Avg HR    | {avg_hr or "N/A"} bpm         |
| Max HR    | {max_hr or "N/A"} bpm         |
| Calories  | {calories or "N/A"} kcal      |
| Elevation | {elevation or "N/A"} m        |
"""]
    if splits:
        lines.append("
## Lap Splits
")
        lines.append("| Lap | Distance | Duration | Avg HR |")
        lines.append("|-----|----------|----------|--------|")
        for i, s in enumerate(splits, 1):
            sdist = meters_to_km(s.get("distance"))
            sdur = secs_to_hms(s.get("duration"))
            shr = s.get("averageHR") or s.get("avgHr", "N/A")
            lines.append(f"| {i} | {sdist} | {sdur} | {shr} |")
    return "
".join(lines)


def fmt_gps_track(points: list, activity_id: int, max_points: int) -> str:
    if not points:
        return f"# GPS Track - Activity {activity_id}

No GPS data found."
    total = len(points)
    step = max(1, total // max_points)
    sampled = points[::step][:max_points]
    lines = [f"# GPS Track - Activity {activity_id}
",
             f"**Total Points:** {total} | **Showing:** {len(sampled)}
",
             "| # | Lat | Lon | Elevation | Time |",
             "|---|-----|-----|-----------|------|"]
    for i, p in enumerate(sampled, 1):
        lat = p.get("lat") or p.get("latitudeDegrees", "")
        lon = p.get("lon") or p.get("longitudeDegrees", "")
        ele = p.get("altitude") or p.get("enhancedAltitude", "")
        t = str(p.get("startTimeGMT") or p.get("time") or "")[:16]
        ele_str = f"{float(ele):.1f}m" if ele else "N/A"
        lines.append(f"| {i} | {lat} | {lon} | {ele_str} | {t} |")
    return "
".join(lines)


def fmt_livetrack(data: dict, token: str) -> str:
    session = data.get("session") or {}
    points = data.get("trackPoints") or []
    name = session.get("displayName", "Unknown")
    activity = session.get("activityType", "Activity")
    start = fmt_date(session.get("sessionStartTime"))
    lines = [f"# LiveTrack - {name}",
             f"**Activity:** {activity} | **Started:** {start}",
             f"**Live URL:** https://livetrack.garmin.com/session/{token}", ""]
    if not points:
        lines.append("No trackpoints yet - activity may not have started.")
        return "
".join(lines)
    latest = points[-1]
    lat = latest.get("lat")
    lon = latest.get("lon")
    speed_kmh = (latest.get("speed") or 0) * 3.6
    elevation = latest.get("altitude")
    ts = fmt_date(latest.get("dateTime"))
    hr = latest.get("heartRate")
    lines += [f"## Latest Position (as of {ts})",
              f"**Coordinates:** {lat}, {lon}",
              f"**Speed:** {speed_kmh:.1f} km/h",
              f"**Elevation:** {elevation or 'N/A'} m",
              f"**Heart Rate:** {hr or 'N/A'} bpm",
              f"**Google Maps:** https://maps.google.com/?q={lat},{lon}",
              f"**Total Points:** {len(points)}"]
    return "
".join(lines)


def fmt_hrv(data: dict, date: str) -> str:
    h = data or {}
    return f"""# HRV - {date}

| Metric      | Value                      |
|-------------|----------------------------|
| Last Night  | {h.get("lastNight5MinHigh") or "N/A"} ms |
| Weekly Avg  | {h.get("weeklyAvg") or "N/A"} ms        |
| Status      | {h.get("status") or "N/A"}              |
| Feedback    | {h.get("feedbackPhrase") or "N/A"}      |
"""


def fmt_training_readiness(data: dict, date: str) -> str:
    t = data if isinstance(data, dict) else {}
    score = t.get("score")
    level = t.get("level")
    feedback = t.get("feedbackLong") or t.get("feedbackShort")
    factors = t.get("primaryFactors") or []
    factor_lines = "
".join(f"- {f}" for f in factors) if factors else "N/A"
    return f"""# Training Readiness - {date}

| Metric | Value              |
|--------|--------------------|
| Score  | {score or "N/A"} / 100 |
| Level  | {level or "N/A"}       |

**Key Factors:**
{factor_lines}

**Feedback:** {feedback or "N/A"}
"""
