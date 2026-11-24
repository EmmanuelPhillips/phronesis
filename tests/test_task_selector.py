from phronesis.database import initialize_database
from phronesis.models import Skill, Task, Attempt
from phronesis.repository import (
    create_learner,
    create_skill,
    create_task,
    create_mastery,
    record_attempt,
)
from phronesis.task_selector import select_next_task


def setup_database(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    learner = create_learner("Test learner", db_path)

    skills = [
        Skill("loops", "Loops", "Understanding iteration"),
        Skill(
            "conditionals",
            "Conditionals",
            "Understanding conditions",
        ),
    ]

    for skill in skills:
        create_skill(skill, db_path)

    tasks = [
        Task(
            id="task-loops",
            title="Loop task",
            description="Test loops",
            code="for i in range(3): print(i)",
            task_type="output",
            difficulty=1,
            expected_answer="0 1 2",
            skill_ids=["loops"],
        ),
        Task(
            id="task-conditionals",
            title="Conditional task",
            description="Test conditions",
            code="if 5 > 3: print('yes')",
            task_type="output",
            difficulty=1,
            expected_answer="yes",
            skill_ids=["conditionals"],
        ),
    ]

    for task in tasks:
        create_task(task, db_path)

    return db_path, learner


def test_selects_task_for_weakest_skill(tmp_path):
    db_path, learner = setup_database(tmp_path)

    create_mastery(learner.id, "loops", 0.80, db_path)
    create_mastery(
        learner.id,
        "conditionals",
        0.35,
        db_path,
    )

    selected = select_next_task(learner.id, db_path)

    assert selected.id == "task-conditionals"


def test_prefers_uncompleted_tasks(tmp_path):
    db_path, learner = setup_database(tmp_path)

    # Make loops the unambiguous weakest skill.
    create_mastery(learner.id, "loops", 0.10, db_path)
    create_mastery(
        learner.id,
        "conditionals",
        0.90,
        db_path,
    )

    attempt = Attempt(
        id="attempt-001",
        learner_id=learner.id,
        task_id="task-loops",
        submitted_answer="0 1 2",
        is_correct=True,
        hints_used=0,
        duration_seconds=10.0,
    )

    record_attempt(attempt, db_path)

    selected = select_next_task(learner.id, db_path)

    # The only loops task has been completed.
    # It should remain available as a fallback.
    assert selected.id == "task-loops"


def test_returns_none_when_no_tasks_exist(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    learner = create_learner("Test learner", db_path)

    assert select_next_task(learner.id, db_path) is None
