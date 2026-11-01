"""A small dependency-aware planner with deterministic topological ordering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class PlanningError(ValueError):
    """Raised when a task graph is incomplete or cyclic."""


@dataclass(frozen=True, slots=True)
class Task:
    """One planned unit of work."""

    task_id: str
    description: str
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task_id must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if self.task_id in self.depends_on:
            raise ValueError("a task cannot depend on itself")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError("task dependencies must be unique")


@dataclass(frozen=True, slots=True)
class Plan:
    """Validated task graph and an executable dependency order."""

    tasks: tuple[Task, ...]
    ordered_task_ids: tuple[str, ...]


class TaskPlanner:
    """Validate dependencies and return a stable topological task order."""

    def build(self, tasks: Iterable[Task]) -> Plan:
        task_list = tuple(tasks)
        by_id = {task.task_id: task for task in task_list}
        if len(by_id) != len(task_list):
            raise PlanningError("task identifiers must be unique")

        for task in task_list:
            missing = set(task.depends_on) - by_id.keys()
            if missing:
                names = ", ".join(sorted(missing))
                raise PlanningError(f"task {task.task_id!r} has missing dependencies: {names}")

        remaining = {task.task_id: set(task.depends_on) for task in task_list}
        ordered: list[str] = []
        original_order = [task.task_id for task in task_list]

        while remaining:
            ready = [
                task_id for task_id in original_order
                if task_id in remaining and not remaining[task_id]
            ]
            if not ready:
                cycle_nodes = ", ".join(
                    task_id for task_id in original_order if task_id in remaining
                )
                raise PlanningError(f"dependency cycle detected among: {cycle_nodes}")

            for task_id in ready:
                ordered.append(task_id)
                remaining.pop(task_id)
            for dependencies in remaining.values():
                dependencies.difference_update(ready)

        return Plan(tasks=task_list, ordered_task_ids=tuple(ordered))
