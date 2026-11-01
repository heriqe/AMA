import pytest

from ama.planning import PlanningError, Task, TaskPlanner


def test_planner_returns_stable_dependency_order():
    tasks = [
        Task("publish", "Publish the approved release", ("test",)),
        Task("test", "Run automated tests", ("build",)),
        Task("build", "Build the package"),
        Task("docs", "Update documentation", ("build",)),
    ]

    plan = TaskPlanner().build(tasks)

    assert plan.ordered_task_ids == ("build", "test", "docs", "publish")


def test_planner_rejects_missing_dependency():
    with pytest.raises(PlanningError, match="missing dependencies"):
        TaskPlanner().build([Task("deploy", "Deploy", ("release",))])


def test_planner_rejects_cycles():
    tasks = [
        Task("a", "Task A", ("b",)),
        Task("b", "Task B", ("a",)),
    ]

    with pytest.raises(PlanningError, match="cycle"):
        TaskPlanner().build(tasks)


def test_planner_rejects_duplicate_ids():
    with pytest.raises(PlanningError, match="unique"):
        TaskPlanner().build([Task("a", "First"), Task("a", "Second")])
