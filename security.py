"""
Security Module - Authentication and Access Control

This module provides the authentication service for the snippet manager.
Handles master password verification, failed attempt tracking, and account
lockout mechanisms to prevent brute-force attacks.

Key Features:
- Master password setup with SHA-256 hashing
- Password verification with attempt tracking
- Automatic lockout after configurable failed attempts
- Time-based lockout expiration
- Automatic reset on successful authentication
"""

from datetime import datetime, timedelta
from storage import ConfigFile, AttemptsFile
from utils import generate_hash

# Timestamp format for attempt tracking and lockout
DATE_FORMAT = "%d-%m-%YT%H:%M:%S"


class AuthService:
    """
    Authentication service for password-protected snippets.

    Manages the master password system that protects locked snippets.
    Implements security features including:
    - One-time password setup
    - Password verification with hashing
    - Failed attempt tracking
    - Automatic account lockout after max attempts
    - Time-based lockout expiration

    The service uses two storage files:
    - config.json: Stores password hash and security settings
    - attempts.json: Tracks failed login attempts and lockout state

    Attributes:
        config (ConfigFile): Configuration file handler
        attempts (AttemptsFile): Attempts tracking file handler

    Security Settings (from config.json):
        max_attempts: Number of failed attempts before lockout (default: 3)
        lockout_duration: Lockout duration in seconds (default: 30)
    """

    def __init__(self, CONFIG_FILE="config.json", ATTEMPTS_FILE="attempts.json"):
        """
        Initialize authentication service.

        Loads configuration and attempts tracking files. Does not verify
        if password is set - use is_initialized() to check.

        Args:
            CONFIG_FILE (str): Config filename (default: config.json)
            ATTEMPTS_FILE (str): Attempts filename (default: attempts.json)
        """
        self.config = ConfigFile(CONFIG_FILE)
        self.attempts = AttemptsFile(ATTEMPTS_FILE)

    def setup(self, master_password: str):
        """
        Set up master password (first-time initialization only).

        Creates a SHA-256 hash of the password and stores it in config.
        Can only be called once - subsequent calls will raise an error.

        Args:
            master_password (str): The master password to set (plain text)

        Returns:
            bool: True on successful setup

        Raises:
            PermissionError: If password is already set (already initialized)

        Note:
            Password is hashed with SHA-256 before storage. The plain text
            password is never stored - only the hash.

        Example:
            auth = AuthService()
            auth.setup("MySecurePassword123")
        """
        # Guard: Prevent re-initialization
        if self.config.is_initialized():
            raise PermissionError("Already initialized")

        # Initialize config structure
        self.config.initialize()

        # Read current config
        config_data = self.config.json_handler.read_all()

        # Hash the password
        master_password_hash = generate_hash(master_password)

        # Store hash and timestamp
        config_data["password_hash"] = master_password_hash
        config_data["created_at"] = datetime.now().strftime(DATE_FORMAT)

        # Persist changes
        self.config.json_handler.write_all(config_data)

        return True

    def verify(self, user_password):
        """
        Verify a password attempt against the stored master password.

        Checks the provided password against the stored hash. Tracks failed
        attempts and enforces lockout policy. Resets attempt counter on success.

        Args:
            user_password (str): Password to verify (plain text)

        Returns:
            bool: True if password matches, False if incorrect

        Raises:
            PermissionError: If master password has not been set up
            ValueError: If account is currently locked out

        Side Effects:
            - Increments failed attempt counter on wrong password
            - Locks account after max attempts reached
            - Resets attempt counter on successful verification

        Example:
            try:
                if auth.verify("password123"):
                    print("Access granted")
                else:
                    print("Wrong password")
            except ValueError as e:
                print(f"Locked out: {e}")
        """
        # Guard: Ensure password is set
        if not self.config.is_initialized():
            raise PermissionError("Config file not initialized")

        # Guard: Check if account is locked
        if self.is_locked_out():
            raise ValueError("Locked out! Try after 30 seconds")

        # Hash input password and compare
        password_hash = generate_hash(user_password)
        if password_hash != self.config.get_master_password_hash():
            # Wrong password - record failure (may trigger lockout)
            self.record_failed_attempts()
            return False

        # Correct password - reset attempts and grant access
        self.attempts.reset()
        return True

    def record_failed_attempts(self):
        """
        Record a failed password attempt and enforce lockout if needed.

        Increments the failed attempt counter. If the counter reaches the
        configured maximum, locks the account for the configured duration.

        Raises:
            ValueError: If max attempts reached (account locked)

        Note:
            This method is called automatically by verify() on failed attempts.
            It should not be called directly under normal circumstances.

        Example:
            After 3 failed attempts:
            - Attempt 1: Counter = 1
            - Attempt 2: Counter = 2
            - Attempt 3: Counter = 3, raises ValueError and sets lockout
        """
        # Load security settings from config
        security = self.config.json_handler.read_all()["security"]

        MAX_ATTEMPTS = security["max_attempts"]
        LOCKOUT_DURATION = security["lockout_duration"]

        # Get current attempt count
        attempts_data = self.attempts.get_data()

        # Increment failed attempts
        failed_attempts = attempts_data["failed_attempts"]
        failed_attempts += 1
        self.attempts.update(failed_attempts=failed_attempts)

        # Check if max attempts reached
        if failed_attempts >= MAX_ATTEMPTS:
            # Calculate lockout expiration time
            locked_until = (
                datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
            ).strftime(DATE_FORMAT)

            # Set lockout
            self.attempts.update(locked_until=locked_until)

            # Raise error to inform caller
            raise ValueError("Locked out! Try after 30 seconds")

    def is_locked_out(self):
        """
        Check if account is currently locked out.

        Verifies lockout status by comparing lockout expiration timestamp
        with current time. Automatically resets lockout if expired.

        Returns:
            bool: True if locked out, False if accessible

        Side Effects:
            - Automatically resets attempts counter if lockout has expired
            - Clears lockout timestamp on expiry

        Example:
            if auth.is_locked_out():
                print("Account is locked. Try again later.")
            else:
                # Allow password attempt
                auth.verify(password)
        """
        # Get lockout timestamp
        locked_until = self.attempts.get_data()["locked_until"]

        # Not locked if no timestamp set
        if not locked_until:
            return False

        # Parse lockout expiration time
        expiry = datetime.strptime(locked_until, DATE_FORMAT)

        # Check if lockout has expired
        if datetime.now() > expiry:
            # Lockout expired - reset and allow access
            self.attempts.reset()
            return False

        # Still locked out
        return True

    def get_lockout_remaining(self):
        """
        Get remaining lockout time in seconds.

        Returns:
            int or None: Seconds remaining in lockout, or None if not locked

        Example:
            remaining = auth.get_lockout_remaining()
            if remaining:
                print(f"Try again in {remaining} seconds")
        """
        locked_until = self.attempts.get_data()["locked_until"]

        if not locked_until:
            return None

        expiry = datetime.strptime(locked_until, DATE_FORMAT)
        remaining = (expiry - datetime.now()).total_seconds()

        return max(0, int(remaining))  # Return 0 if negative

    def get_failed_attempts(self):
        """
        Get current count of failed password attempts.

        Returns:
            int: Number of consecutive failed attempts

        Example:
            attempts = auth.get_failed_attempts()
            print(f"Failed attempts: {attempts}/3")
        """
        return self.attempts.get_data()["failed_attempts"]


if __name__ == "__main__":
    pass
