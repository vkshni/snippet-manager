# Storage Manager

from pathlib import Path
import json
from datetime import datetime

from snippet_entity import Snippet

COUNTER_DATE_FORMAT = "%d%m%Y"

BASE_DIR = Path(__file__).parent


class JSONFile:

    def __init__(self, file_name):
        self.path = self.create(file_name)

    def create(self, file_name):

        path = BASE_DIR / "data" / file_name
        if not path.exists():
            with open(path, "w") as f:
                json.dump({}, f)
        return path

    def read_all(self):

        with open(self.path, "r") as f:

            data = json.load(f)
            return data

    def write_all(self, data):

        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)


class ConfigFile:

    def __init__(self, CONFIG_FILE="config.json"):
        self.json_handler = JSONFile(CONFIG_FILE)

    def _initial_data(self):
        return {
            "password_hash": None,
            "hash_algorithm": "sha256",
            "created_at": None,
            "security": {
                "max_attempts": 3,
                "lockout_duration": 30,
            },
        }

    def initialize(self):

        try:
            data = self.json_handler.read_all()
            if not data:
                self.json_handler.write_all(self._initial_data())
        except:
            self.json_handler.write_all(self._initial_data())

    def is_initialized(self):

        try:
            if self.get_master_password_hash():
                return True
            return False
        except:
            return False

    def get_master_password_hash(self):

        master_password_hash = self.json_handler.read_all()["password_hash"]
        return master_password_hash


class AttempsFile:

    def __init__(self, ATTEMPTS_FILE="attempts.json"):
        self.json_handler = JSONFile(ATTEMPTS_FILE)
        self.initialize()

    def initialize(self):
        try:
            data = self.json_handler.read_all()
            if not data:
                self.reset()
        except:
            self.reset()

    def reset(self):
        self.json_handler.write_all({"failed_attempts": 0, "locked_until": None})
        return True

    def update(self, failed_attempts=None, locked_until=None):

        data = self.json_handler.read_all()
        if failed_attempts is not None:
            data["failed_attempts"] = failed_attempts
        if locked_until is not None:
            data["locked_until"] = locked_until

        self.json_handler.write_all(data)

    def get_data(self):
        data = self.json_handler.read_all()
        return data


class SnippetDB:

    def __init__(self, SNIPPET_FILE="snippets.json"):
        self.json_handler = JSONFile(SNIPPET_FILE)
        self.initialize()

    def initialize(self):

        try:
            data = self.json_handler.read_all()
            if not data:
                self.json_handler.write_all([])
        except:
            self.json_handler.write_all([])

    def add_snippet(self, snippet: Snippet):

        snippets = self.json_handler.read_all()

        snippet_dict = snippet.to_dict()

        snippets.append(snippet_dict)
        self.json_handler.write_all(snippets)
        return True

    def get_all(self) -> list[Snippet]:

        snippets = self.json_handler.read_all()
        snippet_objs = [Snippet.from_dict(s) for s in snippets]
        return snippet_objs

    def update_snippet(self, snippet: Snippet):

        snippets = self.json_handler.read_all()

        updated = False

        for i, s in enumerate(snippets):
            if s["snippet_id"] == snippet.snippet_id:
                snippets[i] = snippet.to_dict()
                updated = True
                break

        self.json_handler.write_all(snippets)
        return updated

    def delete_snippet(self, snippet: Snippet):

        snippets = self.json_handler.read_all()

        filtered = [s for s in snippets if s["snippet_id"] != snippet.snippet_id]

        if len(snippets) == len(filtered):
            return False

        self.json_handler.write_all(filtered)

        return True


if __name__ == "__main__":

    sdb = SnippetDB()
    c = ConfigFile()
    # s1 = Snippet("Code", "if <> else <>")
    # # sdb.add_snippet(s1)
    # s1.snippet_id = "19032026_00007"
    # s1.title = "Other title"
    # s1.status = "ARCHIVED"
    # # print(s1.snippet_id)
    # # # print(sdb.delete_snippet(s1))
    # print(sdb.update_snippet(s1))
    # # config = ConfigFile()
    print(c.get_master_password_hash())
    print(c.is_initialized())
