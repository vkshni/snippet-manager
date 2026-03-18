# Entities
from utils import generate_snippet_id
from datetime import datetime

DATE_FORMAT = "%d-%m-%YT%H:%M:%S"


class Snippet:

    def __init__(
        self,
        title: str,
        content: str,
        tag: str = None,
        created_at: str = None,
        status: str = "ACTIVE",
        access_level: str = "PUBLIC",
        snippet_id: str = None,
    ):

        self.snippet_id = snippet_id if snippet_id else generate_snippet_id()
        self.title = title
        self.content = content
        self.tag = tag.lower() if tag else None
        self.created_at = (
            datetime.strptime(created_at, DATE_FORMAT) if created_at else datetime.now()
        )
        self.status = status
        self.access_level = access_level

    @classmethod
    def from_dict(cls, snippet_dict) -> "Snippet":
        return cls(
            title=snippet_dict["title"],
            content=snippet_dict["content"],
            tag=snippet_dict["tag"],
            created_at=snippet_dict["created_at"],
            status=snippet_dict["status"],
            access_level=snippet_dict["access_level"],
            snippet_id=snippet_dict["snippet_id"],
        )

    def to_dict(self) -> dict:

        return {
            "snippet_id": self.snippet_id,
            "title": self.title,
            "content": self.content,
            "tag": self.tag,
            "created_at": self.created_at.strftime(DATE_FORMAT),
            "status": self.status,
            "access_level": self.access_level,
        }
