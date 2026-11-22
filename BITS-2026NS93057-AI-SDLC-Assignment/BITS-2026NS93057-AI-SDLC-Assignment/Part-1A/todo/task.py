"""Task data and the checks that keep each task valid."""

from typing import List, Optional

from todo.exceptions import TodoError

PRIORITIES = ("low", "medium", "high")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
STATUSES = ("pending", "completed")


def validate_task_id(task_id: object) -> int:
    """Return a task id when it is a positive whole number."""
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise TodoError("Task ID must be a positive whole number.")
    return task_id


def validate_title(title: object) -> str:
    """Return a cleaned title, or raise when the title is blank."""
    if not isinstance(title, str) or not title.strip():
        raise TodoError("Title is required.")
    return title.strip()


def validate_description(description: object) -> str:
    """Return a cleaned description. An empty description is allowed."""
    if description is None:
        return ""
    if not isinstance(description, str):
        raise TodoError("Description must be text.")
    return description.strip()


def validate_priority(priority: object) -> str:
    """Return a priority of low, medium, or high."""
    if not isinstance(priority, str):
        raise TodoError("Priority must be low, medium, or high.")
    cleaned = priority.strip().lower()
    if cleaned not in PRIORITIES:
        raise TodoError("Priority must be low, medium, or high.")
    return cleaned


def validate_status(status: object) -> str:
    """Return a status of pending or completed."""
    if not isinstance(status, str):
        raise TodoError("Status must be pending or completed.")
    cleaned = status.strip().lower()
    if cleaned not in STATUSES:
        raise TodoError("Status must be pending or completed.")
    return cleaned


def validate_tags(tags: Optional[object]) -> List[str]:
    """Return a list of tags.

    Tags may be given as a list or as one comma-separated string.
    Blank tags and repeated tags are removed.
    """
    if tags is None:
        return []
    if isinstance(tags, str):
        items = tags.split(",")
    elif isinstance(tags, list):
        items = tags
    else:
        raise TodoError("Tags must be a list of text values.")

    cleaned: List[str] = []
    seen = set()
    for item in items:
        if not isinstance(item, str):
            raise TodoError("Each tag must be text.")
        tag = item.strip()
        if not tag:
            continue
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(tag)
    return cleaned


class Task:
    """One todo item stored by the application."""

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str = "",
        priority: str = "medium",
        tags: Optional[object] = None,
        status: str = "pending",
    ) -> None:
        self.task_id = validate_task_id(task_id)
        self.title = validate_title(title)
        self.description = validate_description(description)
        self.priority = validate_priority(priority)
        self.tags = validate_tags(tags)
        self.status = validate_status(status)

    @property
    def ticket_id(self) -> int:
        return self.task_id

    @ticket_id.setter
    def ticket_id(self, value: int) -> None:
        self.task_id = value

    @property
    def Ticket_Summary(self) -> str:
        return self.title

    @Ticket_Summary.setter
    def Ticket_Summary(self, value: str) -> None:
        self.title = value

    @property
    def Ticket_description(self) -> str:
        return self.description

    @Ticket_description.setter
    def Ticket_description(self, value: str) -> None:
        self.description = value

    @property
    def Severity(self) -> str:
        return self.priority

    @Severity.setter
    def Severity(self, value: str) -> None:
        self.priority = value

    def to_dict(self) -> dict:
        """Return this task as plain data that can be saved as JSON."""
        return {
            "ticket_id": self.task_id,
            "Ticket_Summary": self.title,
            "Ticket_description": self.description,
            "Severity": self.priority,
            "tags": list(self.tags),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: object) -> "Task":
        """Build a task from data that was read from the JSON file."""
        if not isinstance(data, dict):
            raise TodoError("Each task must be a JSON object.")
        ticket_id = data.get("ticket_id", data.get("task_id"))
        title = data.get("Ticket_Summary", data.get("title"))
        description = data.get("Ticket_description", data.get("description"))
        priority = data.get("Severity", data.get("priority"))
        tags = data.get("tags")
        status = data.get("status")

        required = (
            "ticket_id",
            "Ticket_Summary",
            "Ticket_description",
            "Severity",
            "tags",
            "status",
        )
        missing = []
        if ticket_id is None:
            missing.append("ticket_id")
        if title is None:
            missing.append("Ticket_Summary")
        if description is None:
            missing.append("Ticket_description")
        if priority is None:
            missing.append("Severity")
        if "tags" not in data:
            missing.append("tags")
        if "status" not in data:
            missing.append("status")

        if missing:
            names = ", ".join(missing)
            raise TodoError(f"Task is missing: {names}.")
        return cls(
            task_id=ticket_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            status=status,
        )
