# Snippet Manager
from storage import SnippetDB
from snippet_entity import Snippet


class SnippetManager:

    def __init__(self, SNIPPET_FILE="snippets.json"):
        self.snippet_db = SnippetDB(SNIPPET_FILE)

    def add_snippet(self, title, content, tag=None):

        snippet_obj = Snippet(title, content, tag)

        self.snippet_db.add_snippet(snippet_obj)
        return True

    def get_snippet_by_title(self, title):

        snippets = self.snippet_db.get_all()
        filtered = [s for s in snippets if s.title.lower() == title.lower()]
        return filtered


if __name__ == "__main__":
    sm = SnippetManager()
    # sm.add_snippet("Python", "Coding....")
    s = sm.get_snippet_by_title("Pythn")
    print(s)
