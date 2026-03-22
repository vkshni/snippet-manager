"""
Utilities Module - Helper Functions

This module provides utility functions used throughout the snippet manager:
- Unique ID generation with date-based prefixes
- Password hashing with SHA-256

These utilities are stateless and can be imported and used anywhere in the application.
"""

from datetime import datetime
import hashlib
from counter_storage import CounterFile

# Date format for ID generation (DDMMYYYY)
COUNTER_DATE_FORMAT = "%d%m%Y"

# Global counter instance - maintains state across all ID generations
counter = CounterFile()


def generate_snippet_id():
    """
    Generate a unique snippet ID with date prefix and sequential counter.

    Creates IDs in the format: DDMMYYYY_NNNNN
    - Date part: Current date in DDMMYYYY format
    - Counter part: 5-digit zero-padded sequential number

    The counter resets to 1 each day, allowing for up to 99,999 snippets per day.
    If the counter exceeds 99,999, the formatting will expand beyond 5 digits.

    Returns:
        str: Unique snippet ID (e.g., "22032026_00001", "22032026_00042")

    Side Effects:
        - Increments the global counter
        - Updates counter file on disk
        - May reset counter to 1 if date changes

    Examples:
        First snippet of the day:
        >>> generate_snippet_id()
        "22032026_00001"

        Second snippet:
        >>> generate_snippet_id()
        "22032026_00002"

        Next day, counter resets:
        >>> generate_snippet_id()
        "23032026_00001"

    Note:
        The counter is stored persistently in counter.json and survives
        program restarts. However, it resets daily to keep IDs readable.
    """
    # Get current date
    current_date = datetime.now().strftime(COUNTER_DATE_FORMAT)

    # Read current counter state
    counter_data = counter.read_all()

    # Check if we're still on the same date
    if current_date == counter_data["last_date"]:
        # Same day - increment counter
        next_id = counter_data["last_id"] + 1
        counter_data["last_id"] = next_id

    elif current_date > counter_data["last_date"]:
        # New day - reset counter to 1
        counter_data["last_date"] = current_date
        next_id = 1
        counter_data["last_id"] = next_id

    # Persist updated counter
    counter.write_all(counter_data)

    # Format: DDMMYYYY_NNNNN (5-digit zero-padded counter)
    return f"{current_date}_{next_id:05d}"


def generate_hash(password_str):
    """
    Generate SHA-256 hash of a password string.

    Creates a secure one-way hash of the input string. The same input
    will always produce the same hash, but the hash cannot be reversed
    to recover the original password.

    Args:
        password_str (str): Password or text to hash (plain text)

    Returns:
        str: 64-character hexadecimal SHA-256 hash

    Security:
        - Uses SHA-256 algorithm (256-bit hash)
        - No salt is added (consider adding for production systems)
        - Hash is deterministic (same input = same output)
        - Irreversible (cannot recover password from hash)

    Examples:
        >>> generate_hash("password123")
        "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"

        >>> generate_hash("password123")  # Same input
        "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"  # Same output

        >>> generate_hash("different")
        "dd1ab6b0fb8a49a0e184e6c443d89e8d8d5e3ff3a64054fe15dbedb7c3a2f26e"  # Different output

    Note:
        For production use, consider using a salted hash algorithm like
        bcrypt or argon2 instead of plain SHA-256.
    """
    # Encode string to bytes
    password_bytes = password_str.encode()

    # Generate SHA-256 hash
    password_hash = hashlib.sha256(password_bytes).hexdigest()

    return password_hash


if __name__ == "__main__":
    pass
