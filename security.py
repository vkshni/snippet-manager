from datetime import datetime, timedelta
from storage import ConfigFile, AttempsFile
from utils import generate_hash

DATE_FORMAT = "%d-%m-%YT%H:%M:%S"


class AuthService:

    def __init__(self, CONFIG_FILE="config.json", ATTEMPTS_FILE="attempts.json"):
        self.config = ConfigFile(CONFIG_FILE)
        self.attempts = AttempsFile(ATTEMPTS_FILE)

    def setup(self, master_password: str):

        if self.config.is_initialized():
            raise PermissionError("Already initialized")

        self.config.initialize()

        config_data = self.config.json_handler.read_all()

        master_password_hash = generate_hash(master_password)

        config_data["password_hash"] = master_password_hash
        config_data["created_at"] = datetime.now().strftime(DATE_FORMAT)

        self.config.json_handler.write_all(config_data)
        return True

    def verify(self, user_password):

        if not self.config.is_initialized():
            raise PermissionError("Config file not initialized")

        if self.is_locked_out():
            raise ValueError("Locked out! Try after 30 seconds")

        password_hash = generate_hash(user_password)
        if password_hash != self.config.get_master_password_hash():
            self.record_failed_attempts()
            return False

        self.attempts.reset()
        return True

    def record_failed_attempts(self):

        security = self.config.json_handler.read_all()["security"]

        MAX_ATTEMPTS = security["max_attempts"]
        LOCKOUT_DURATION = security["lockout_duration"]

        attempts_data = self.attempts.get_data()

        failed_attempts = attempts_data["failed_attempts"]
        failed_attempts += 1
        self.attempts.update(failed_attempts=failed_attempts)

        if failed_attempts >= MAX_ATTEMPTS:
            locked_until = (
                datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
            ).strftime(DATE_FORMAT)
            self.attempts.update(locked_until=locked_until)
            raise ValueError("Locked out! Try after 30 seconds")

    def is_locked_out(self):

        locked_until = self.attempts.get_data()["locked_until"]

        if not locked_until:
            return False

        expiry = datetime.strptime(locked_until, DATE_FORMAT)

        if datetime.now() > expiry:
            self.attempts.reset()
            return False

        return True


if __name__ == "__main__":
    auth = AuthService()
    # auth.setup("vks1234")
    print(auth.verify("vks1234"))
