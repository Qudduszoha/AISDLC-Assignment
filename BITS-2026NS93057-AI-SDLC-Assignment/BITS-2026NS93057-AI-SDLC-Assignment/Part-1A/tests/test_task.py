"""Tests for task validation and JSON conversion."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from todo.exceptions import TodoError
from todo.task import Task


def test_task_round_trip_drops_duplicate_tags():
    task = Task(1, " Read ", " Chapter 2 ", "HIGH", ["study", "Study"], "pending")
    copy = Task.from_dict(task.to_dict())
    assert copy.to_dict() == task.to_dict()
    assert task.title == "Read"
    assert task.priority == "high"
    assert task.tags == ["study"]


def test_rejects_blank_title():
    with pytest.raises(TodoError, match="Title is required"):
        Task(1, "   ")


def test_rejects_bad_priority():
    with pytest.raises(TodoError, match="Priority"):
        Task(1, "Read", priority="urgent")


def test_rejects_bad_status():
    with pytest.raises(TodoError, match="Status"):
        Task(1, "Read", status="done")


def test_from_dict_missing_field():
    with pytest.raises(TodoError, match=r"(?i)(title|Ticket_Summary)"):
        Task.from_dict({"ticket_id": 1})


def test_rejects_non_numeric_task_id():
    with pytest.raises(TodoError, match="Task ID"):
        Task("1", "Read")


def test_task_title_with_surrounding_whitespace_is_trimmed():
    task = Task(1, "  Clean Room  ")
    assert task.title == "Clean Room"


def test_task_rejects_non_string_title():
    with pytest.raises(TodoError, match="Title is required"):
        Task(1, 12345)


def test_task_description_none_becomes_empty_string():
    task = Task(1, "Valid Title", description=None)
    assert task.description == ""


def test_task_description_trimmed():
    task = Task(1, "Valid Title", description="  Detailed description  ")
    assert task.description == "Detailed description"


def test_task_rejects_non_string_description():
    with pytest.raises(TodoError, match="Description must be text"):
        Task(1, "Valid Title", description=999)


def test_task_priority_case_insensitive():
    task = Task(1, "Valid Title", priority="  HIGH  ")
    assert task.priority == "high"


def test_task_priority_all_valid_levels():
    for p in ["low", "medium", "high", "LOW", "Medium", "HIGH"]:
        task = Task(1, "Valid Title", priority=p)
        assert task.priority == p.strip().lower()


def test_task_status_case_insensitive():
    task = Task(1, "Valid Title", status="  COMPLETED  ")
    assert task.status == "completed"


def test_task_status_all_valid_levels():
    for s in ["pending", "completed", "PENDING", "COMPLETED"]:
        task = Task(1, "Valid Title", status=s)
        assert task.status == s.strip().lower()


def test_task_tags_comma_separated_string():
    task = Task(1, "Valid Title", tags="alpha, beta, gamma")
    assert task.tags == ["alpha", "beta", "gamma"]


def test_task_tags_none_returns_empty_list():
    task = Task(1, "Valid Title", tags=None)
    assert task.tags == []


def test_task_tags_drops_empty_entries():
    task = Task(1, "Valid Title", tags="first, , second,   , third")
    assert task.tags == ["first", "second", "third"]


def test_task_rejects_tags_invalid_type():
    with pytest.raises(TodoError, match="Tags must be a list"):
        Task(1, "Valid Title", tags=123)


def test_task_rejects_non_string_tag_in_list():
    with pytest.raises(TodoError, match="Each tag must be text"):
        Task(1, "Valid Title", tags=["valid", 123])


def test_task_properties_ticket_tokens():
    task = Task(1, "Original", "Desc", "low", ["t1"], "pending")
    assert task.ticket_id == 1
    assert task.Ticket_Summary == "Original"
    assert task.Ticket_description == "Desc"
    assert task.Severity == "low"

    task.ticket_id = 10
    task.Ticket_Summary = "Modified"
    task.Ticket_description = "New Desc"
    task.Severity = "high"

    assert task.task_id == 10
    assert task.title == "Modified"
    assert task.description == "New Desc"
    assert task.priority == "high"
