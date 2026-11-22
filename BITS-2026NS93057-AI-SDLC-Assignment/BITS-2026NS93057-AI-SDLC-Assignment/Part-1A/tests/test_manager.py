"""Tests for creating, changing, filtering, and sorting tasks."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from todo.exceptions import TodoError
from todo.manager import ActivityProductManager, TodoManager


def test_create_list_and_ids(Product_Mgr):
    first = Product_Mgr.create_task("Buy milk", "2 litres", "high", ["home"])
    second = Product_Mgr.create_task("Read chapter", priority="low", tags="study, uni")
    assert first.task_id == 1
    assert first.status == "pending"
    assert second.task_id == 2
    assert second.tags == ["study", "uni"]
    assert [task.task_id for task in Product_Mgr.list_tasks()] == [1, 2]


def test_create_rejects_blank_title(Product_Mgr):
    with pytest.raises(TodoError, match="Title is required"):
        Product_Mgr.create_task("   ")


def test_update_task(Product_Mgr):
    task = Product_Mgr.create_task("Draft", priority="low")
    updated = Product_Mgr.update_task(
        task.task_id,
        title="Final draft",
        description="Add tests",
        priority="high",
        tags=["uni"],
    )
    assert updated.title == "Final draft"
    assert updated.description == "Add tests"
    assert updated.priority == "high"
    assert updated.tags == ["uni"]


def test_invalid_priority_does_not_change_task(Product_Mgr):
    task = Product_Mgr.create_task("Draft", priority="low")
    with pytest.raises(TodoError, match="Priority"):
        Product_Mgr.update_task(task.task_id, priority="urgent")
    saved = Product_Mgr.get_task(task.task_id)
    assert saved.priority == "low"
    assert saved.title == "Draft"


def test_delete_task(Product_Mgr):
    task = Product_Mgr.create_task("Temp")
    deleted = Product_Mgr.delete_task(task.task_id)
    assert deleted.title == "Temp"
    assert Product_Mgr.list_tasks() == []


def test_delete_missing_task(Product_Mgr):
    with pytest.raises(TodoError, match="not found"):
        Product_Mgr.delete_task(5)


def test_mark_completed(Product_Mgr):
    task = Product_Mgr.create_task("Lab report")
    done = Product_Mgr.mark_completed(task.task_id)
    assert done.status == "completed"
    again = Product_Mgr.mark_completed(task.task_id)
    assert again.status == "completed"


def test_filter_by_tag_is_case_insensitive(Product_Mgr):
    Product_Mgr.create_task("Essay", tags=["Uni", "writing"])
    Product_Mgr.create_task("Shop", tags=["home"])
    found = Product_Mgr.filter_by_tag(" uni ")
    assert [task.title for task in found] == ["Essay"]


def test_filter_requires_a_tag(Product_Mgr):
    with pytest.raises(TodoError, match="Tag is required"):
        Product_Mgr.filter_by_tag("   ")


def test_sort_by_priority(Product_Mgr):
    Product_Mgr.create_task("Low one", priority="low")
    Product_Mgr.create_task("High one", priority="high")
    Product_Mgr.create_task("Medium one", priority="medium")
    Product_Mgr.create_task("High two", priority="high")
    ordered = Product_Mgr.sort_by_priority()
    assert [task.title for task in ordered] == [
        "High one",
        "High two",
        "Medium one",
        "Low one",
    ]


def test_sort_can_be_saved(Product_Mgr):
    Product_Mgr.create_task("Low one", priority="low")
    Product_Mgr.create_task("High one", priority="high")
    Product_Mgr.sort_by_priority(save=True)
    assert [task.title for task in Product_Mgr.list_tasks()] == [
        "High one",
        "Low one",
    ]


def test_tasks_are_reloaded_from_json(tmp_path):
    path = tmp_path / "tasks.json"
    original = ActivityProductManager(path)
    original.create_task("Persist me", tags=["save"])
    original.mark_completed(1)

    reloaded = ActivityProductManager(path)
    task = reloaded.get_task(1)
    assert task.title == "Persist me"
    assert task.status == "completed"
    assert task.tags == ["save"]
    assert reloaded.create_task("Next").task_id == 2


def test_create_multiple_tasks_increments_id(Product_Mgr):
    t1 = Product_Mgr.create_task("Task 1")
    t2 = Product_Mgr.create_task("Task 2")
    t3 = Product_Mgr.create_task("Task 3")
    assert [t1.task_id, t2.task_id, t3.task_id] == [1, 2, 3]
    assert len(Product_Mgr.list_tasks()) == 3


def test_get_existing_task(Product_Mgr):
    created = Product_Mgr.create_task("Target task", "Specific desc", "high")
    fetched = Product_Mgr.get_task(created.task_id)
    assert fetched.title == "Target task"
    assert fetched.description == "Specific desc"
    assert fetched.priority == "high"


def test_get_non_existent_task_raises_error(Product_Mgr):
    with pytest.raises(TodoError, match="not found"):
        Product_Mgr.get_task(999)


def test_get_task_rejects_non_integer(Product_Mgr):
    with pytest.raises(TodoError, match="positive whole number"):
        Product_Mgr.get_task("abc")


def test_update_task_description_only(Product_Mgr):
    task = Product_Mgr.create_task("Title Only", "Old desc", "medium")
    updated = Product_Mgr.update_task(task.task_id, description="New desc")
    assert updated.description == "New desc"
    assert updated.title == "Title Only"
    assert updated.priority == "medium"


def test_update_task_tags_only(Product_Mgr):
    task = Product_Mgr.create_task("Task with tags", tags=["initial"])
    updated = Product_Mgr.update_task(task.task_id, tags=["new", "tags"])
    assert updated.tags == ["new", "tags"]
    assert updated.title == "Task with tags"


def test_update_task_status_to_pending(Product_Mgr):
    task = Product_Mgr.create_task("Task to complete")
    Product_Mgr.mark_completed(task.task_id)
    reopened = Product_Mgr.update_task(task.task_id, status="pending")
    assert reopened.status == "pending"


def test_update_non_existent_task_raises_error(Product_Mgr):
    with pytest.raises(TodoError, match="not found"):
        Product_Mgr.update_task(999, title="Does not exist")


def test_delete_only_target_task_in_multi_list(Product_Mgr):
    Product_Mgr.create_task("Task 1")
    t2 = Product_Mgr.create_task("Task 2")
    Product_Mgr.create_task("Task 3")
    Product_Mgr.delete_task(t2.task_id)
    remaining_ids = [t.task_id for t in Product_Mgr.list_tasks()]
    assert remaining_ids == [1, 3]


def test_filter_by_tag_no_matching_tasks(Product_Mgr):
    Product_Mgr.create_task("Task 1", tags=["home"])
    Product_Mgr.create_task("Task 2", tags=["personal"])
    found = Product_Mgr.filter_by_tag("work")
    assert found == []


def test_filter_by_tag_multiple_matches(Product_Mgr):
    Product_Mgr.create_task("Task A", tags=["backend", "python"])
    Product_Mgr.create_task("Task B", tags=["frontend", "python"])
    Product_Mgr.create_task("Task C", tags=["ops"])
    found = Product_Mgr.filter_by_tag("python")
    assert len(found) == 2
    assert [t.title for t in found] == ["Task A", "Task B"]


def test_sort_by_priority_stable_with_equal_priorities(Product_Mgr):
    t1 = Product_Mgr.create_task("First high", priority="high")
    t2 = Product_Mgr.create_task("Second high", priority="high")
    ordered = Product_Mgr.sort_by_priority()
    assert [t.task_id for t in ordered] == [t1.task_id, t2.task_id]


def test_sort_by_priority_without_saving(Product_Mgr):
    Product_Mgr.create_task("Low task", priority="low")
    Product_Mgr.create_task("High task", priority="high")
    Product_Mgr.sort_by_priority(save=False)
    assert [t.title for t in Product_Mgr.list_tasks()] == ["Low task", "High task"]


def test_create_task_with_whitespace_title_is_trimmed(Product_Mgr):
    task = Product_Mgr.create_task("   Whitespace Title   ")
    assert task.title == "Whitespace Title"


def test_create_task_default_priority_is_medium(Product_Mgr):
    task = Product_Mgr.create_task("Default Priority")
    assert task.priority == "medium"
