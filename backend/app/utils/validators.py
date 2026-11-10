"""Input validation utilities and regex patterns."""

import re
from datetime import date, datetime
from typing import Optional, Union

# Robust RFC 5322 compliant simplified email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

VALID_GENDERS = {"M", "F", "O"}


def is_valid_email(email: Optional[str]) -> bool:
    """Validate email format using regular expression."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def clean_name(name: Optional[str]) -> str:
    """Strip extraneous whitespace and apply title-casing."""
    if not name or not isinstance(name, str):
        return ""
    # Collapses multiple inner spaces into single space and title-cases
    cleaned = " ".join(name.strip().split())
    return cleaned.title()


def parse_date(value: Union[str, date, datetime, None]) -> Optional[date]:
    """Parse string or datetime object into a date object."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in ("nan", "none", "null", "nat"):
            return None
        # Try common date formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    return None


def clip_percentage(value: Optional[float]) -> Optional[float]:
    """Clip numeric percentage value strictly to [0.0, 100.0]. Returns None if impossible."""
    if value is None:
        return None
    try:
        val = float(value)
        if val < 0.0 or val > 100.0:
            return None
        return round(val, 2)
    except (ValueError, TypeError):
        return None
