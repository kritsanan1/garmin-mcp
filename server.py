"""
server.py — Garmin MCP Server (FastMCP / OpenClaw · Port 8422)

Tools:
  1.  garmin_get_daily_summary
  2.  garmin_get_heart_rate
  3.  garmin_get_steps
  4.  garmin_get_sleep
  5.  garmin_get_stress
  6.  garmin_get_body_battery
  7.  garmin_list_activities
  8.  garmin_get_activity_details
  9.  garmin_get_gps_track
  10. garmin_get_livetrack
  11. garmin_get_hrv
  12. garmin_get_training_readiness
"""

import logging
import os

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from garmin_client import date_range, garmin, today_str
from models import (
    ActivityDetailsInput, BodyBatteryInput, DailySummaryInput, GpsTrackInput,
    HeartRateInput, HrvInput, ListActivitiesInput, LiveTrackInput,
    ResponseFormat, SleepInput, StepsInput, StressInput, TrainingReadinessInput,
)
from utils import (
    fmt_activity_details, fmt_body_battery, fmt_daily_summary, fmt_gps_track,
    fmt_heart_rate, fmt_hrv, fmt_livetrack, fmt_sleep, fmt_steps, fmt_stress,
    fmt_training_readiness, fmt_activities, to_json,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("garmin_mcp")

mcp = FastMCP(
    name="garmin_mcp",
    instructions=(
        "Garmin Connect integration: real-time GPS (LiveTrack), HR, sleep, stress, "
        "body battery, steps, HRV, training readiness, and full activity history. "
        "All date parameters default to today. Get activity IDs from garmin_list_activities."
    ),
)
PORT = int(os.environ.get("GARMIN_MCP_PORT", 8422))


@mcp.tool(name="garmin_get_daily_summary", annotations={"title": "Get Daily Health Summary", "readOnlyHint": True})
async def garmin_get_daily_summary(params: DailySummaryInput) -> str:
    """Full daily health snapshot: steps, resting HR, stress, body battery, calories, distance, sleep."""
    try:
        data = garmin.call("get_stats", params.date)
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_daily_summary(data or {}, params.date)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_heart_rate", annotations={"title": "Get Heart Rate Data", "readOnlyHint": True})
async def garmin_get_heart_rate(params: HeartRateInput) -> str:
    """Heart rate data: resting HR, daily max/min, and time-series samples."""
    try:
        data = garmin.call("get_heart_rates", params.date)
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_heart_rate(data or {}, params.date)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_steps", annotations={"title": "Get Steps & Activity Data", "readOnlyHint": True})
async def garmin_get_steps(params: StepsInput) -> str:
    """Step count in 15-minute intervals with activity level classification."""
    try:
        data = garmin.call("get_steps_data", params.date)
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_steps(data or [], params.date)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_sleep", annotations={"title": "Get Sleep Analysis", "readOnlyHint": True})
async def garmin_get_sleep(params: SleepInput) -> str:
    """Sleep stages (deep/light/REM/awake), bedtime, wake time, and sleep score."""
    try:
        data = garmin.call("get_sleep_data", params.date)
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_sleep(data or {}, params.date)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_stress", annotations={"title": "Get Stress Levels", "readOnlyHint": True})
async def garmin_get_stress(params: StressInput) -> str:
    """Stress levels with ASCII timeline. Scale: 0-25 resting, 26-50 low, 51-75 medium, 76-100 high."""
    try:
        data = garmin.call("get_stress_data", params.date)
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_stress(data or {}, params.date)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_body_battery", annotations={"title": "Get Body Battery", "readOnlyHint": True})
async def garmin_get_body_battery(params: BodyBatteryInput) -> str:
    """Body Battery (0-100) energy levels over a date range. Max 7 days."""
    try:
        dates = date_range(params.start_date, params.end_date)
        data = garmin.call("get_body_battery", dates)
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_body_battery(data or [])
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_list_activities", annotations={"title": "List Recent Activities", "readOnlyHint": True})
async def garmin_list_activities(params: ListActivitiesInput) -> str:
    """List recent activities with ID, type, date, distance, duration. Use IDs for drill-down."""
    try:
        data = garmin.call("get_activities", params.offset, params.limit)
        if params.activity_type:
            data = [a for a in (data or []) if params.activity_type.lower() in
                    ((a.get("activityType") or {}).get("typeKey", "") if isinstance(a.get("activityType"), dict)
                     else str(a.get("activityType", ""))).lower()]
        return to_json(data) if params.response_format == ResponseFormat.JSON else fmt_activities(data or [])
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_activity_details", annotations={"title": "Get Activity Details", "readOnlyHint": True})
async def garmin_get_activity_details(params: ActivityDetailsInput) -> str:
    """Full activity stats: pace, HR, calories, elevation, and optional lap splits."""
    try:
        activity = garmin.call("get_activity", params.activity_id)
        splits = []
        if params.include_splits:
            try:
                splits_data = garmin.call("get_activity_splits", params.activity_id)
                splits = splits_data.get("lapDTOs") or splits_data.get("splits") or []
            except Exception:
                pass
        if params.response_format == ResponseFormat.JSON:
            return to_json({"activity": activity, "splits": splits})
        return fmt_activity_details(activity or {}, splits)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_gps_track", annotations={"title": "Get GPS Track", "readOnlyHint": True})
async def garmin_get_gps_track(params: GpsTrackInput) -> str:
    """GPS coordinates (lat/lon/elevation/time) from a recorded activity."""
    try:
        details = garmin.call("get_activity_details", params.activity_id)
        measurements = (
            details.get("gpsPoints")
            or details.get("measurementDataList")
            or details.get("activityTrackingData", {}).get("trackPoints")
            or []
        )
        if not measurements:
            metrics = details.get("activityDetailMetrics") or []
            measurements = [
                {"lat": m.get("metrics", {}).get("LAT"), "lon": m.get("metrics", {}).get("LON"),
                 "altitude": m.get("metrics", {}).get("ALTITUDE"), "time": m.get("startTimeGMT")}
                for m in metrics if m.get("metrics", {}).get("LAT")
            ]
        if params.response_format == ResponseFormat.JSON:
            return to_json({"activityId": params.activity_id, "gpsPoints": measurements})
        return fmt_gps_track(measurements, params.activity_id, params.max_points)
    except RuntimeError as e:
        return f"Error: {e}"


LIVETRACK_BASE = "https://livetrack.garmin.com/services/session"


@mcp.tool(name="garmin_get_livetrack", annotations={"title": "Get Real-time LiveTrack Position", "readOnlyHint": True, "idempotentHint": False})
async def garmin_get_livetrack(params: LiveTrackInput) -> str:
    """Poll Garmin LiveTrack for real-time GPS position during an active activity.

    Get session_token from your LiveTrack share URL:
    https://livetrack.garmin.com/session/{TOKEN}/token/...
    Call repeatedly — updates every ~4 seconds.
    """
    try:
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 (compatible; garmin_mcp/1.0)"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            session_resp = await client.get(f"{LIVETRACK_BASE}/{params.session_token}/session", headers=headers)
            session_resp.raise_for_status()
            points_resp = await client.get(
                f"{LIVETRACK_BASE}/{params.session_token}/trackpoints?from=1&to={params.max_points}", headers=headers)
            points_resp.raise_for_status()
        combined = {"session": session_resp.json().get("session") or session_resp.json(),
                    "trackPoints": points_resp.json().get("trackPoints") or points_resp.json()}
        if params.response_format == ResponseFormat.JSON:
            return to_json(combined)
        return fmt_livetrack(combined, params.session_token)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return "LiveTrack session not found. Check the token and ensure the activity is live."
        return f"LiveTrack HTTP error: {e.response.status_code}"
    except Exception as e:
        return f"LiveTrack error: {e}"


@mcp.tool(name="garmin_get_hrv", annotations={"title": "Get HRV Data", "readOnlyHint": True})
async def garmin_get_hrv(params: HrvInput) -> str:
    """HRV (Heart Rate Variability): last-night value, weekly average, and recovery status."""
    try:
        data = garmin.call("get_hrv_data", params.date)
        if params.response_format == ResponseFormat.JSON:
            return to_json(data)
        hrv = data.get("hrvSummary") if isinstance(data, dict) else data or {}
        return fmt_hrv(hrv or {}, params.date)
    except RuntimeError as e:
        return f"Error: {e}"


@mcp.tool(name="garmin_get_training_readiness", annotations={"title": "Get Training Readiness Score", "readOnlyHint": True})
async def garmin_get_training_readiness(params: TrainingReadinessInput) -> str:
    """Training Readiness score (0-100): sleep + HRV + training load + stress + body battery."""
    try:
        data = garmin.call("get_training_readiness", params.date)
        if params.response_format == ResponseFormat.JSON:
            return to_json(data)
        item = data[0] if isinstance(data, list) and data else data or {}
        return fmt_training_readiness(item, params.date)
    except RuntimeError as e:
        return f"Error: {e}"


if __name__ == "__main__":
    logger.info("Garmin MCP Server starting on port %d ...", PORT)
    mcp.run(transport="streamable-http", port=PORT)
