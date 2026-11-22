"""Tests for the command line interface."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from todo.cli import main


def test_cli_create_complete_and_list(tmp_path, monkeypatch, capsys):
    answers = iter(
        [
            "1",
            "Submit report",
            "Part 1A",
            "high",
            "uni, assignment",
            "5",
            "1",
            "2",
            "8",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"

    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Created task 1." in output
    assert "Submit report" in output
    assert "Task 1 marked as completed." in output
    assert "Status:      completed" in output
    assert path.exists()


def test_cli_exit_immediately(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "8")
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Goodbye." in output


def test_cli_invalid_option_then_exit(tmp_path, monkeypatch, capsys):
    answers = iter(["99", "8"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Please choose a number from 1 to 8." in output
    assert "Goodbye." in output


def test_cli_empty_list_initially(tmp_path, monkeypatch, capsys):
    answers = iter(["2", "8"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "No tasks found." in output


def test_cli_delete_task_confirmed(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Buy groceries", "Milk, Bread", "medium", "home",
        "4", "1", "y",
        "2",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Created task 1." in output
    assert "Deleted task 1." in output
    assert "No tasks found." in output


def test_cli_delete_task_cancelled(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Important task", "Do not delete", "high", "",
        "4", "1", "n",
        "2",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Delete cancelled." in output
    assert "Important task" in output


def test_cli_update_task(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Initial title", "Initial desc", "low", "tag1",
        "3", "1", "Updated title", "", "high", "", "",
        "2",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Updated task 1." in output
    assert "Updated title" in output
    assert "Priority:    high" in output


def test_cli_filter_by_tag(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Work meeting", "Sprint plan", "high", "work, project",
        "1", "Grocery shop", "Apples", "low", "personal",
        "6", "work",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Work meeting" in output
    assert "Grocery shop" not in output.split("1 task(s):")[-1]


def test_cli_sort_tasks(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Low item", "", "low", "",
        "1", "High item", "", "high", "",
        "7",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Tasks sorted by priority (high, medium, then low)." in output


def test_cli_eof_handled(tmp_path, monkeypatch, capsys):
    def raise_eof(_prompt):
        raise EOFError()

    monkeypatch.setattr("builtins.input", raise_eof)
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Goodbye." in output


def test_cli_keyboard_interrupt_handled(tmp_path, monkeypatch, capsys):
    def raise_sigint(_prompt):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", raise_sigint)
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Goodbye." in output


def test_cli_prompt_task_id_non_digit_error(tmp_path, monkeypatch, capsys):
    answers = iter(["5", "not_a_number", "8"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Error: Task ID must be a positive whole number." in output


def test_cli_corrupt_file_startup_failure(tmp_path, capsys):
    path = tmp_path / "corrupt.json"
    path.write_text("{ invalid json ...", encoding="utf-8")
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 1
    assert "Error: Could not read" in output


def test_cli_create_with_defaults(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Task with defaults", "", "", "",
        "2",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Priority:    medium" in output
    assert "Description: -" in output
    assert "Tags:        -" in output


def test_cli_filter_no_match(tmp_path, monkeypatch, capsys):
    answers = iter([
        "1", "Task with tag", "", "medium", "urgent",
        "6", "nonexistent",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "No tasks found." in output


def test_cli_delete_non_existent_id(tmp_path, monkeypatch, capsys):
    answers = iter([
        "4", "999",
        "8",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    path = tmp_path / "tasks.json"
    exit_code = main(["--file", str(path)])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Error: Task 999 was not found." in output
