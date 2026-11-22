"""R&D Ticket Tracking Management package."""

from todo.manager import (
    ActivityProductManager,
    ActivityProductManager as TodoManager,
    ActivityProductManager as Product_Mgr,
)
from todo.task import Task

__all__ = ["Task", "ActivityProductManager", "TodoManager", "Product_Mgr"]

