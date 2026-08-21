"""UTC ISO-8601 normalization for announcement timestamps.

All stored / compared timestamps use the same shape as JS `Date.toISOString()`:
  YYYY-MM-DDTHH:MM:SS.sssZ  (milliseconds, always UTC, always Z suffix)

This keeps DynamoDB string range compares (`publishAt <= now`) correct across
Python `isoformat()` (microseconds) and browser `toISOString()` (milliseconds).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union

DateInput = Union[str, datetime, None]


def parse_to_utc(value: DateInput) -> Optional[datetime]:
    """Parse a timestamp into an aware UTC datetime, or None if empty."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return None
        # fromisoformat (3.11+) accepts Z; older runtimes need +00:00
        if text.endswith('Z'):
            text = text[:-1] + '+00:00'
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def normalize_utc_iso(value: DateInput) -> Optional[str]:
    """Normalize to `YYYY-MM-DDTHH:MM:SS.sssZ`, or None if empty/invalid input is empty."""
    dt = parse_to_utc(value)
    if dt is None:
        return None
    ms = dt.microsecond // 1000
    return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{ms:03d}Z'


def now_utc_iso() -> str:
    """Current UTC time in the canonical announcement timestamp format."""
    # normalize_utc_iso never returns None for datetime input
    return normalize_utc_iso(datetime.now(timezone.utc))  # type: ignore[return-value]
