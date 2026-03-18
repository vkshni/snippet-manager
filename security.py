from datetime import datetime
from storage import ConfigFile, AttempsFile
from utils import generate_hash

DATE_FORMAT = "%d-%m-%YT%H:%M:%S"


class AuthService:

    def __init__(self, CONFIG_FILE="config.json", ATTEMPTS_FILE="attempts.json"):
        self.config = ConfigFile(CONFIG_FILE)
        self.attempts = AttempsFile(ATTEMPTS_FILE)

    def setup(self, master_password: str):

        config_data = self.config.json_handler.read_all()
        if config_data["password_hash"]:
            raise ValueError("Config file exists")

        master_password_hash = generate_hash(master_password)

        config_data["password_hash"] = master_password_hash
        config_data["created_at"] = datetime.now().strftime(DATE_FORMAT)

        self.config.json_handler.write_all(config_data)
        return True

    def record_failed_attempts(self):

        MAX_ATTEMPTS = self.config.json_handler.read_all()["max_attempts"]
        attempts_data = self.attempts.json_handler.read_all()
        failed_attempts = attempts_data["failed_attempts"]
        failed_attempts += 1
        self.attempts.json_handler.write_all(attempts_data)

        if failed_attempts >= MAX_ATTEMPTS:
            locked_until = 300
            attempts_data["locked_until"]
            self.attempts.json_handler.write_all(attempts_data)
            raise ValueError("Locked out")

    def verify(self, user_password):

        password_hash = generate_hash(user_password)
        if password_hash == self.config.json_handler.read_all()["password_hash"]:
            return True

        self.record_failed_attempts()
        raise ValueError("Incorrect Password")


if __name__ == "__main__":
    auth = AuthService()
    # auth.setup("vks1234")
    print(auth.verify("vks123"))
