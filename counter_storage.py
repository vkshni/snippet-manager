# counter storage
from pathlib import Path
import json
from datetime import datetime

COUNTER_DATE_FORMAT = "%d%m%Y"

BASE_DIR = Path(__file__).parent


class CounterFile:

    def __init__(self, COUNTER_FILE="counter.json"):
        self.path = BASE_DIR / "data" / COUNTER_FILE
        self.initialize()

    def initialize(self):
        try:
            data = self.read_all()
            if not data:
                self.write_all(
                    {
                        "last_id": 0,
                        "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
                    }
                )
        except:
            self.write_all(
                {
                    "last_id": 0,
                    "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
                }
            )

    def read_all(self):

        with open(self.path, "r") as f:

            data = json.load(f)
            return data

    def write_all(self, data):

        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
