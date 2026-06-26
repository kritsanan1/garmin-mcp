"""
models.py
Pydantic v2 input validation models for every Garmin MCP tool.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from garmin_client import today_str


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class BaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class DailySummaryInput(BaseInput):
    date: str = Field(default_factory=today_str, description="Date YYYY-MM-DD (defaults to today)")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        from datetime import datetime
        datetime.strptime(v, "%Y-%m-%d")
        return v


class HeartRateInput(BaseInput):
    date: str = Field(default_factory=today_str)


class StepsInput(BaseInput):
    date: str = Field(default_factory=today_str)


class SleepInput(BaseInput):
    date: str = Field(default_factory=today_str, description="Wake-up date YYYY-MM-DD")


class StressInput(BaseInput):
    date: str = Field(default_factory=today_str)


class BodyBatteryInput(BaseInput):
    start_date: str = Field(default_factory=today_str)
    end_date: str = Field(default_factory=today_str, description="Max 7 days from start")

    @field_validator("end_date")
    @classmethod
    def validate_range(cls, v: str, info) -> str:
        from datetime import datetime
        start = info.data.get("start_date")
        if start:
            if (datetime.strptime(v, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days > 7:
                raise ValueError("Date range cannot exceed 7 days")
        return v


class ListActivitiesInput(BaseInput):
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)
    activity_type: Optional[str] = Field(default=None, description="e.g. running, cycling, swimming")


class ActivityDetailsInput(BaseInput):
    activity_id: int = Field(..., gt=0, description="From garmin_list_activities")
    include_splits: bool = Field(default=True)


class GpsTrackInput(BaseInput):
    activity_id: int = Field(..., gt=0)
    max_points: int = Field(default=200, ge=10, le=2000)


class LiveTrackInput(BaseInput):
    session_token: str = Field(..., min_length=10, description="Token from LiveTrack share URL")
    max_points: int = Field(default=50, ge=1, le=500)


class HrvInput(BaseInput):
    date: str = Field(default_factory=today_str)


class TrainingReadinessInput(BaseInput):
    date: str = Field(default_factory=today_str)
