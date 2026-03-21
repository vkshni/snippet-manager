# Snippet Manager
from storage import SnippetDB
from snippet_entity import Snippet
from security import AuthService


class SnippetManager:

    def __init__(
        self,
        SNIPPET_FILE="snippets.json",
        CONFIG_FILE="config.json",
        ATTEMPTS_FILE="attempts.json",
    ):
        self.snippet_db = SnippetDB(SNIPPET_FILE)
        self.auth = AuthService(CONFIG_FILE, ATTEMPTS_FILE)

    def add_snippet(self, title, content, tag=None, access_level="PUBLIC"):

        snippet_obj = Snippet(title.strip(), content, tag, access_level=access_level)

        self.snippet_db.add_snippet(snippet_obj)
        return snippet_obj

    def list_all(self, status="ACTIVE"):

        snippets = self.snippet_db.get_all()
        filtered = [s for s in snippets if s.status == status]
        return filtered

    def list_by_tag(self, tag=None, status="ACTIVE"):

        snippets = self.snippet_db.get_all()
        filtered = [
            s for s in snippets if s.tag == tag.lower() and s.status == status.upper()
        ]
        return filtered

    def get_snippet_by_title(self, title, status="ACTIVE"):

        snippets = self.snippet_db.get_all()
        if not snippets:
            raise ValueError("No snippets found")

        filtered = [
            s
            for s in snippets
            if s.title.lower() == title.lower() and s.status == status
        ]

        if not filtered:
            raise ValueError(f"Snippet with title '{title}' not found")

        return filtered

    def get_snippet_by_id(self, snippet_id: str):

        snippets = self.snippet_db.get_all()
        if not snippets:
            raise ValueError("No snippets found")

        for s in snippets:
            if s.snippet_id == snippet_id:
                return s

        return None

    def archive_snippet(self, snippet_id: str):

        snippet = self.get_snippet_by_id(snippet_id)

        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # check if already archived
        if snippet.status == "ARCHIVED":
            raise ValueError(f"Snippet with ID '{snippet_id}' already archived")

        # archive if not
        snippet.status = "ARCHIVED"

        self.snippet_db.update_snippet(snippet)

        return True

    def unarchive_snippet(self, snippet_id: str):

        snippet = self.get_snippet_by_id(snippet_id)

        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # check if already unarchived
        if snippet.status == "ACTIVE":
            raise ValueError(f"Snippet with ID '{snippet_id}' already unarchived")

        # archive if not
        snippet.status = "ACTIVE"

        self.snippet_db.update_snippet(snippet)

        return True

    def lock_snippet(self, snippet_id: str):

        snippet = self.get_snippet_by_id(snippet_id)
        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # check if already locked
        if snippet.access_level == "LOCKED":
            raise ValueError(f"Snippet with ID '{snippet_id}' already locked")

        # lock if not
        snippet.access_level = "LOCKED"

        self.snippet_db.update_snippet(snippet)
        return True

    def unlock_snippet(self, snippet_id: str):

        snippet = self.get_snippet_by_id(snippet_id)
        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # check if already unlocked
        if snippet.access_level == "PUBLIC":
            raise ValueError(f"Snippet with ID '{snippet_id}' already unlocked")

        # unlock if not
        snippet.access_level = "PUBLIC"

        self.snippet_db.update_snippet(snippet)
        return True

    def search_snippet(self, keyword: str, status: str = "ACTIVE"):

        snippets = self.snippet_db.get_all()

        filtered = list()
        for s in snippets:
            if s.status == "ACTIVE" and (
                keyword.lower() in s.title.lower()
                or (s.tag and keyword.lower() in s.tag.lower())
            ):
                filtered.append(s)
        return filtered

    def is_archived(self, snippet: Snippet):
        return snippet.status == "ARCHIVED"

    def is_locked(self, snippet: Snippet):
        return snippet.access_level == "LOCKED"


if __name__ == "__main__":
    sm = SnippetManager()
    # sm.add_snippet("Python", "Coding....")
    # s = sm.get_snippet_by_title("Pythn")
    # s = sm.get_snippet_by_id("19032026_00008")
    # print(s.title, s.content)
    # print(sm.archive_snippet("19032026_00007"))
    # print(sm.unlock_snippet(s.snippet_id))

    results = sm.search_snippet("python")
    for s in results:
        print(s.title, s.content)
