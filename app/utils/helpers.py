"""Common helper utilities used across the application."""

import hashlib
import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


def generate_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string.

    Args:
        length: Length of the random string.

    Returns:
        Random alphanumeric string.
    """
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_referral_code(length: int = 8) -> str:
    """Generate a unique referral code.

    Args:
        length: Length of the code (default 8).

    Returns:
        Uppercase alphanumeric referral code.
    """
    return secrets.token_urlsafe(length).upper().replace("_", "").replace("-", "")[:length]


def hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt for production).

    Args:
        password: Plain text password.

    Returns:
        Hashed password.
    """
    salt = "mednear_ai_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash.

    Args:
        password: Plain text password.
        hashed: Hashed password.

    Returns:
        True if matches, False otherwise.
    """
    return hash_password(password) == hashed


def mask_card_number(card_number: str) -> str:
    """Mask sensitive card number, showing only last 4 digits.

    Args:
        card_number: Full card number.

    Returns:
        Masked card number like '**** **** **** 1234'.
    """
    cleaned = re.sub(r"\s+", "", card_number)
    if len(cleaned) < 4:
        return "*" * len(cleaned)
    return f"**** **** **** {cleaned[-4:]}"


def mask_phone_number(phone: str) -> str:
    """Mask phone number, keeping country code and last 2 digits.

    Args:
        phone: Phone number string.

    Returns:
        Masked phone number.
    """
    if len(phone) <= 4:
        return "*" * len(phone)
    return phone[:4] + "*" * (len(phone) - 6) + phone[-2:]


def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date.

    Args:
        birth_date: Date of birth.

    Returns:
        Age in years.
    """
    today = datetime.now()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def format_currency(amount: float, currency: str = "UZS") -> str:
    """Format amount with currency symbol.

    Args:
        amount: Numeric amount.
        currency: Currency code.

    Returns:
        Formatted currency string.
    """
    symbols = {"UZS": "so'm", "USD": "$", "EUR": "€", "RUB": "₽"}
    symbol = symbols.get(currency, currency)
    formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")
    return f"{formatted} {symbol}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length.

    Args:
        text: Original text.
        max_length: Maximum length.
        suffix: Suffix to add if truncated.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)].strip() + suffix


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection.

    Args:
        text: Raw user input.

    Returns:
        Sanitized text.
    """
    if not text:
        return ""

    replacements = {
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "&": "&amp;",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text.strip()


def is_valid_email(email: str) -> bool:
    """Check if email format is valid.

    Args:
        email: Email address.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Check if phone number format is valid (international).

    Args:
        phone: Phone number.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r"^\+?[1-9]\d{7,14}$"
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(re.match(pattern, cleaned))


def parse_duration(duration_str: str) -> Optional[int]:
    """Parse duration string like '1h', '30m', '2d' to minutes.

    Args:
        duration_str: Duration string (e.g., '1h', '30m', '2d').

    Returns:
        Duration in minutes or None if invalid.
    """
    pattern = r"^(\d+)([mhd])$"
    match = re.match(pattern, duration_str.lower().strip())
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)

    multipliers = {"m": 1, "h": 60, "d": 1440}
    return value * multipliers.get(unit, 1)


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size.

    Args:
        items: List to chunk.
        chunk_size: Size of each chunk.

    Returns:
        List of chunks.
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get(data: Dict, *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value.

    Args:
        data: Dictionary to search.
        keys: Sequence of keys to traverse.
        default: Default value if key not found.

    Returns:
        Value or default.
    """
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def get_time_range(days: int = 7) -> tuple:
    """Get date range for last N days.

    Args:
        days: Number of days.

    Returns:
        Tuple of (start_date, end_date).
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    return start, end


def log_execution(func):
    """Decorator to log function execution time and errors."""

    async def async_wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = datetime.utcnow()
        try:
            logger.debug(f"Executing {func_name}...")
            result = await func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.debug(f"{func_name} completed in {duration:.3f}s")
            return result
        except Exception as e:
            logger.error(f"{func_name} failed: {e}", exc_info=True)
            raise

    def sync_wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = datetime.utcnow()
        try:
            logger.debug(f"Executing {func_name}...")
            result = func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.debug(f"{func_name} completed in {duration:.3f}s")
            return result
        except Exception as e:
            logger.error(f"{func_name} failed: {e}", exc_info=True)
            raise

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


__all__ = [
    "generate_random_string",
    "generate_referral_code",
    "hash_password",
    "verify_password",
    "mask_card_number",
    "mask_phone_number",
    "calculate_age",
    "format_currency",
    "truncate_text",
    "sanitize_input",
    "is_valid_email",
    "is_valid_phone",
    "parse_duration",
    "chunk_list",
    "safe_get",
    "get_time_range",
    "log_execution",
]