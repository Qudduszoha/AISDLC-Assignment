"""Shared test setup."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from todo.manager import ActivityProductManager  # noqa: E402


@pytest.fixture
def Product_Mgr(tmp_path):
    """Return a Product_Mgr that stores tasks in a temporary file."""
    return ActivityProductManager(tmp_path / "tasks.json")


@pytest.fixture
def manager(Product_Mgr):
    """Backward-compatible fixture."""
    return Product_Mgr
