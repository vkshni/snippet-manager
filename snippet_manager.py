# Snippet Manager
from storage import SnippetDB
from snippet_entity import Snippet


class SnippetManager:

    def __init__(self, SNIPPET_FILE="snippets.json"):
        self.snippet_db = SnippetDB(SNIPPET_FILE)

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
            raise ValueError(f"Snippet with titel '{title}' not found")

        return filtered


if __name__ == "__main__":
    sm = SnippetManager()
    # sm.add_snippet("Python", "Coding....")
    s = sm.get_snippet_by_title("Pythn")
    print(s)
