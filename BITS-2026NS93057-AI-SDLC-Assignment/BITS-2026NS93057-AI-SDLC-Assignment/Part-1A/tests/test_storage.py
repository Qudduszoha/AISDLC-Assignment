"""Tests for the JSON storage file."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from todo.exceptions import TodoError
from todo.storage import JsonStorage
from todo.task import Task


def test_missing_file_starts_empty(tmp_path):
    tasks, next_id = JsonStorage(tmp_path / "missing.json").load()
    assert tasks == []
    assert next_id == 1


def test_empty_file_starts_empty(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text("  \n", encoding="utf-8")
    tasks, next_id = JsonStorage(path).load()
    assert tasks == []
    assert next_id == 1


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "nested" / "tasks.json"
    storage = JsonStorage(path)
    tasks = [Task(1, "One", "desc", "medium", ["a"], "pending")]
    storage.save(tasks, 2)
    loaded, next_id = storage.load()
    assert next_id == 2
    assert loaded[0].to_dict() == tasks[0].to_dict()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved.get("Dev id", saved.get("next_id")) == 2
    tickets = saved.get("Tickets", saved.get("tasks"))
    assert tickets[0].get("Ticket_Summary", tickets[0].get("title")) == "One"


def test_invalid_json(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text("[", encoding="utf-8")
    with pytest.raises(TodoError, match="invalid JSON"):
        JsonStorage(path).load()


def test_next_id_moves_past_existing_tasks(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps(
            {
                "Dev id": 1,
                "Tickets": [
                    {
                        "ticket_id": 4,
                        "Ticket_Summary": "Old",
                        "Ticket_description": "",
                        "Severity": "low",
                        "tags": [],
                        "status": "pending",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    tasks, next_id = JsonStorage(path).load()
    assert tasks[0].task_id == 4
    assert next_id == 5


def test_load_non_dict_json_raises_error(tmp_path):
    path = tmp_path / "array.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(TodoError, match="must contain an object"):
        JsonStorage(path).load()


def test_load_missing_tickets_key_raises_error(tmp_path):
    path = tmp_path / "no_tickets.json"
    path.write_text(json.dumps({"Dev id": 1}), encoding="utf-8")
    with pytest.raises(TodoError, match="missing the Tickets list"):
        JsonStorage(path).load()


def test_load_tickets_not_a_list_raises_error(tmp_path):
    path = tmp_path / "bad_tickets.json"
    path.write_text(json.dumps({"Tickets": "string_not_list"}), encoding="utf-8")
    with pytest.raises(TodoError, match="missing the Tickets list"):
        JsonStorage(path).load()


def test_load_invalid_dev_id_type_boolean(tmp_path):
    path = tmp_path / "bool_id.json"
    path.write_text(json.dumps({"Tickets": [], "Dev id": True}), encoding="utf-8")
    with pytest.raises(TodoError, match="positive whole number"):
        JsonStorage(path).load()


def test_load_invalid_dev_id_negative(tmp_path):
    path = tmp_path / "neg_id.json"
    path.write_text(json.dumps({"Tickets": [], "Dev id": -1}), encoding="utf-8")
    with pytest.raises(TodoError, match="positive whole number"):
        JsonStorage(path).load()


def test_load_invalid_dev_id_zero(tmp_path):
    path = tmp_path / "zero_id.json"
    path.write_text(json.dumps({"Tickets": [], "Dev id": 0}), encoding="utf-8")
    with pytest.raises(TodoError, match="positive whole number"):
        JsonStorage(path).load()


def test_load_invalid_dev_id_string(tmp_path):
    path = tmp_path / "str_id.json"
    path.write_text(json.dumps({"Tickets": [], "Dev id": "abc"}), encoding="utf-8")
    with pytest.raises(TodoError, match="positive whole number"):
        JsonStorage(path).load()


def test_save_creates_nested_directories(tmp_path):
    nested_path = tmp_path / "d1" / "d2" / "d3" / "storage.json"
    storage = JsonStorage(nested_path)
    storage.save([], 1)
    assert nested_path.exists()


def test_save_overwrites_existing_file(tmp_path):
    path = tmp_path / "tasks.json"
    storage = JsonStorage(path)
    task1 = Task(1, "First")
    storage.save([task1], 2)
    task2 = Task(2, "Second")
    storage.save([task1, task2], 3)
    loaded, next_id = storage.load()
    assert len(loaded) == 2
    assert next_id == 3


def test_save_validates_next_id_positive(tmp_path):
    path = tmp_path / "tasks.json"
    storage = JsonStorage(path)
    with pytest.raises(TodoError, match="positive whole number"):
        storage.save([], -5)


def test_save_validates_next_id_not_bool(tmp_path):
    path = tmp_path / "tasks.json"
    storage = JsonStorage(path)
    with pytest.raises(TodoError, match="positive whole number"):
        storage.save([], True)


def test_load_legacy_tasks_key_fallback(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps(
            {
                "next_id": 2,
                "tasks": [
                    {
                        "ticket_id": 1,
                        "Ticket_Summary": "Legacy Task",
                        "Ticket_description": "",
                        "Severity": "low",
                        "tags": [],
                        "status": "pending",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    loaded, next_id = JsonStorage(path).load()
    assert len(loaded) == 1
    assert loaded[0].title == "Legacy Task"
    assert next_id == 2


def test_load_empty_tickets_list(tmp_path):
    path = tmp_path / "empty_tickets.json"
    path.write_text(json.dumps({"Tickets": [], "Dev id": 10}), encoding="utf-8")
    loaded, next_id = JsonStorage(path).load()
    assert loaded == []
    assert next_id == 10


def test_load_dev_id_auto_increments_past_max_ticket_id(tmp_path):
    path = tmp_path / "adjust_id.json"
    path.write_text(
        json.dumps(
            {
                "Dev id": 2,
                "Tickets": [
                    {
                        "ticket_id": 5,
                        "Ticket_Summary": "Task Five",
                        "Ticket_description": "",
                        "Severity": "medium",
                        "tags": [],
                        "status": "pending",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    loaded, next_id = JsonStorage(path).load()
    assert loaded[0].task_id == 5
    assert next_id == 6


def test_save_replaces_atomic_temp_file(tmp_path):
    path = tmp_path / "atomic.json"
    storage = JsonStorage(path)
    storage.save([], 1)
    temp_file = path.with_suffix(".tmp")
    assert not temp_file.exists()
    assert path.exists()
