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


class CounterFile:

    def __init__(self, COUNTER_FILE="counter.json"):
        self.json_handler = JSONFile(COUNTER_FILE)
        self.initialize()

    def initialize(self):
        try:
            data = self.json_handler.read_all()
            if not data:
                self.json_handler.write_all(
                    {
                        "last_id": 0,
                        "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
                    }
                )
        except:
            self.json_handler.write_all(
                {
                    "last_id": 0,
                    "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
                }
            )


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

    def update_snippet(self, snippet: Snippet):

        snippets = self.json_handler.read_all()

        updated = False

        for i, s in enumerate(snippets):
            if s["snippet_id"] == snippet.snippet_id:
                s[i] = snippet.to_dict()
                updated = True
                break

        self.json_handler.write_all(snippets)
        return updated

    def delete_snippet(self, snippet: Snippet):

        snippets = self.json_handler.read_all()

        filtered = [s for s in snippets if s["snippet_id"] != snippet.snippet_id]

        if len(snippets) == len(filtered):
            return False

        return True


if __name__ == "__main__":

    sdb = SnippetDB()
    s1 = Snippet("Code", "if <> else <>")
    sdb.add_snippet(s1)
