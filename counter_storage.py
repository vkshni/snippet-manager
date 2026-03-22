"""
Counter Storage - Sequential ID Generator

This module manages a persistent counter for generating unique sequential IDs.
The counter maintains state across program restarts by storing the last generated
ID number in a JSON file.

Used by the ID generator to create time-based unique identifiers in the format:
DDMMYYYY_NNNNN (e.g., 22032026_00001)
"""

from pathlib import Path
import json
from datetime import datetime

# Date format for counter tracking (DDMMYYYY)
COUNTER_DATE_FORMAT = "%d%m%Y"

# Base directory - parent directory of this file
BASE_DIR = Path(__file__).parent


class CounterFile:
    """
    Persistent counter manager for generating sequential IDs.

    Maintains a running counter that survives program restarts. Stores both
    the last generated ID number and the date it was generated.

    The counter is continuous (doesn't reset daily) to ensure global uniqueness
    of IDs across all time periods.

    Attributes:
        path (Path): Full path to the counter.json file

    Storage Format:
        {
            "last_id": 42,              # Last generated ID number
            "last_date": "22032026"     # Date of last ID (DDMMYYYY)
        }
    """

    def __init__(self, COUNTER_FILE="counter.json"):
        """
        Initialize counter file handler.

        Creates the data directory if it doesn't exist and initializes
        the counter file with default values if needed.

        Args:
            COUNTER_FILE (str): Counter filename (default: counter.json)
        """
        self.path = BASE_DIR / "data" / COUNTER_FILE

        # Create data directory if it doesn't exist (handles edge case)
        self.path.parent.mkdir(exist_ok=True)

        # Initialize counter file
        self.initialize()

    def initialize(self):
        """
        Initialize counter file with default values if empty or corrupted.

        Sets up initial counter state:
        - last_id: 0 (next ID will be 1)
        - last_date: Current date in DDMMYYYY format

        Safe to call multiple times - only initializes if needed.
        """
        try:
            data = self.read_all()
            if not data:
                # File is empty - initialize with defaults
                self.write_all(
                    {
                        "last_id": 0,
                        "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
                    }
                )
        except:
            # File is corrupted or doesn't exist - reset to defaults
            self.write_all(
                {
                    "last_id": 0,
                    "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
                }
            )

    def read_all(self):
        """
        Read counter data from file.

        Returns:
            dict: Counter data containing 'last_id' and 'last_date'

        Raises:
            json.JSONDecodeError: If file contains invalid JSON
            FileNotFoundError: If file doesn't exist

        Example:
            data = counter.read_all()
            print(data["last_id"])    # 42
            print(data["last_date"])  # "22032026"
        """
        with open(self.path, "r") as f:
            data = json.load(f)
            return data

    def write_all(self, data):
        """
        Write counter data to file.

        Overwrites the entire counter file with new data.
        Uses 4-space indentation for readability.

        Args:
            data (dict): Counter data with 'last_id' and 'last_date' keys

        Example:
            counter.write_all({
                "last_id": 43,
                "last_date": "22032026"
            })
        """
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def get_next_id(self):
        """
        Get the next sequential ID number and increment the counter.

        Reads the current counter, increments it, saves it back, and returns
        the new value. This ensures each call produces a unique, sequential ID.

        Returns:
            int: Next sequential ID number (starts at 1)

        Note:
            This method has a side effect - it permanently increments the counter.
            The counter is continuous and never resets, even across different dates.

        Example:
            id1 = counter.get_next_id()  # Returns 1
            id2 = counter.get_next_id()  # Returns 2
            id3 = counter.get_next_id()  # Returns 3
        """
        # Read current counter state
        data = self.read_all()

        # Increment counter
        next_id = data["last_id"] + 1

        # Update stored values
        data["last_id"] = next_id
        data["last_date"] = datetime.now().strftime(COUNTER_DATE_FORMAT)

        # Persist changes
        self.write_all(data)

        return next_id

    def reset(self):
        """
        Reset counter to zero.

        Resets the counter back to its initial state (last_id = 0).
        Next generated ID will be 1.

        Warning:
            This can cause ID collisions if old IDs are still in use.
            Only use for testing or complete data reset scenarios.

        Returns:
            bool: True on success
        """
        self.write_all(
            {
                "last_id": 0,
                "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
            }
        )
        return True

    def get_current_count(self):
        """
        Get the current counter value without incrementing.

        Useful for checking the counter state or determining how many
        IDs have been generated.

        Returns:
            int: Current counter value (last generated ID number)

        Example:
            count = counter.get_current_count()
            print(f"Generated {count} IDs so far")
        """
        data = self.read_all()
        return data["last_id"]
