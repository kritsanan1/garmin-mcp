"""
garmin_client.py
Garmin Connect API client with session caching and auto-reconnect.
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

logger = logging.getLogger(__name__)

TOKEN_STORE_PATH = Path(
    os.environ.get("GARMIN_TOKEN_STORE", Path.home() / ".garmin_mcp_tokens")
)


class GarminClient:
    """Thread-safe Garmin Connect API client with session persistence."""

    def __init__(self) -> None:
        self._api: Optional[Garmin] = None

    def _load_credentials(self) -> tuple[str, str]:
        email = os.environ.get("GARMIN_EMAIL", "")
        password = os.environ.get("GARMIN_PASSWORD", "")
        if not email or not password:
            raise RuntimeError(
                "GARMIN_EMAIL and GARMIN_PASSWORD must be set in environment. "
                "Copy .env.example to .env and fill in your credentials."
            )
        return email, password

    def _fresh_login(self) -> Garmin:
        email, password = self._load_credentials()
        logger.info("Logging in to Garmin Connect as %s ...", email)
        api = Garmin(email=email, password=password)
        api.login()
        TOKEN_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        token_data = api.garth.dumps()
        TOKEN_STORE_PATH.write_text(token_data)
        logger.info("Session cached at %s", TOKEN_STORE_PATH)
        return api

    def _resume_login(self) -> Garmin:
        token_data = TOKEN_STORE_PATH.read_text()
        api = Garmin()
        api.login(tokenstore=token_data)
        logger.info("Resumed Garmin session from cache")
        return api

    def get_api(self) -> Garmin:
        """Return authenticated Garmin API, logging in if necessary."""
        if self._api is not None:
            return self._api
        if TOKEN_STORE_PATH.exists():
            try:
                self._api = self._resume_login()
                return self._api
            except Exception as exc:
                logger.warning("Cached session invalid (%s) — re-logging in", exc)
        self._api = self._fresh_login()
        return self._api

    def reset(self) -> None:
        """Force re-authentication on next call."""
        self._api = None
        if TOKEN_STORE_PATH.exists():
            TOKEN_STORE_PATH.unlink()

    def call(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Call a Garmin API method with automatic retry on auth expiry."""
        for attempt in range(2):
            try:
                api = self.get_api()
                method = getattr(api, method_name)
                return method(*args, **kwargs)
            except GarminConnectAuthenticationError as exc:
                if attempt == 0:
                    logger.warning("Auth expired, re-authenticating...")
                    self.reset()
                    continue
                raise RuntimeError(f"Garmin authentication failed: {exc}") from exc
            except GarminConnectTooManyRequestsError as exc:
                raise RuntimeError("Garmin rate limit hit. Wait a few minutes.") from exc
            except GarminConnectConnectionError as exc:
                raise RuntimeError(f"Cannot connect to Garmin servers: {exc}") from exc
            except Exception as exc:
                raise RuntimeError(f"Garmin API error ({method_name}): {exc}") from exc
        raise RuntimeError("Garmin call failed after retry")


def today_str() -> str:
    return datetime.today().strftime("%Y-%m-%d")


def date_range(start: str, end: str) -> list[str]:
    """Return list of ISO date strings from start to end inclusive."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    days = (end_dt - start_dt).days + 1
    return [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]


garmin = GarminClient()
