from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reminder_agent import ReminderAgent


REFERENCE = datetime(2026, 11, 21, 12, 0, 0)


def test_create_reminder():
    response = ReminderAgent().process("Remind me to call Software_Dev tomorrow at 5 PM", REFERENCE)
    assert response["intent"] == "create_reminder"
    assert response["task"] == "call Software_Dev"
    assert response["datetime"] == "2026-11-22T17:00:00"
    assert response["needs_clarification"] is False


def test_missing_time_requires_clarification():
    response = ReminderAgent().process("Remind me about the meeting", REFERENCE)
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None
    assert response["needs_clarification"] is True


def test_invalid_date_requires_clarification():
    response = ReminderAgent().process("Remind me to file taxes on February 30 at 9 AM", REFERENCE)
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None


def test_empty_input_requires_clarification():
    response = ReminderAgent().process("", REFERENCE)
    assert response["intent"] == "clarification_required"


def test_reschedule_intent():
    response = ReminderAgent().process(
        "reschedule meeting to tomorrow at 3 PM",
        REFERENCE,
    )
    assert response["intent"] == "reschedule_reminder"
    assert response["datetime"] == "2026-11-22T15:00:00"
    assert response["needs_clarification"] is False


def test_snooze_intent_minutes():
    response = ReminderAgent().process("snooze for 15 minutes", REFERENCE)
    assert response["intent"] == "snooze_reminder"
    assert response["datetime"] == "2026-11-21T12:15:00"
    assert response["needs_clarification"] is False


def test_snooze_intent_hours():
    response = ReminderAgent().process("snooze for 2 hours", REFERENCE)
    assert response["intent"] == "snooze_reminder"
    assert response["datetime"] == "2026-11-21T14:00:00"
    assert response["needs_clarification"] is False


def test_nonsense_input_requires_clarification():
    response = ReminderAgent().process("qwerty", REFERENCE)
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None


def test_asdf_input_requires_clarification():
    response = ReminderAgent().process("asdf", REFERENCE)
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None


def test_contradictory_dates_requires_clarification():
    response = ReminderAgent().process(
        "remind me to run tomorrow and Friday at 10 AM",
        REFERENCE,
    )
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None


def test_relative_minutes_creation():
    response = ReminderAgent().process(
        "Remind me to drink water in 45 minutes",
        REFERENCE,
    )
    assert response["intent"] == "create_reminder"
    assert response["task"] == "drink water"
    assert response["datetime"] == "2026-11-21T12:45:00"


def test_iso_date_creation():
    response = ReminderAgent().process(
        "Please remind me to submit report on 2026-12-01 at 09:30",
        REFERENCE,
    )
    assert response["intent"] == "create_reminder"
    assert "submit report" in response["task"]
    assert response["datetime"] == "2026-12-01T09:30:00"


def test_relative_today_creation():
    response = ReminderAgent().process(
        "Remind me about team standup today at 9 AM",
        REFERENCE,
    )
    assert response["intent"] == "create_reminder"
    assert response["task"] == "team standup"
    assert response["datetime"] == "2026-11-21T09:00:00"


def test_full_month_date_creation():
    response = ReminderAgent().process(
        "Remind me to renew passport on January 15, 2027 at 10 AM",
        REFERENCE,
    )
    assert response["intent"] == "create_reminder"
    assert response["task"] == "renew passport"
    assert response["datetime"] == "2027-01-15T10:00:00"


def test_weekday_creation():
    response = ReminderAgent().process(
        "Remind me to attend yoga next Friday at 7 PM",
        REFERENCE,
    )
    assert response["intent"] == "create_reminder"
    assert response["task"] == "attend yoga"
    assert response["needs_clarification"] is False


def test_invalid_hour_requires_clarification():
    response = ReminderAgent().process("Remind me to sleep at 25:00 tomorrow", REFERENCE)
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None


def test_invalid_april_31_requires_clarification():
    response = ReminderAgent().process(
        "Remind me to pay bills on April 31 at 10 AM",
        REFERENCE,
    )
    assert response["intent"] == "clarification_required"
    assert response["datetime"] is None


def test_whitespace_only_input_requires_clarification():
    response = ReminderAgent().process("      ", REFERENCE)
    assert response["intent"] == "clarification_required"


def test_default_reference_datetime():
    response = ReminderAgent().process("Remind me to take a break in 30 minutes")
    assert response["intent"] == "create_reminder"
    assert response["task"] == "take a break"
    assert response["datetime"] is not None
