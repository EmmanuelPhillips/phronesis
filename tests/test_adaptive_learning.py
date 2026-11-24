from phronesis.models import Attempt
from phronesis.repository import (
    create_learner,
    create_mastery,
    get_all_tasks,
    get_mastery,
    record_attempt,
)
from phronesis.seed import seed_database
from phronesis.learner_service import update_learner_mastery
from phronesis.task_selector import select_next_task


def test_learner_performance_influences_next_task(tmp_path):
    # Arrange: create an isolated database and seed it.
    db_path = tmp_path / "test_phronesis.db"
    seed_database(db_path)

    learner = create_learner(
        "Integration learner",
        db_path=db_path,
        learner_id="integration-learner",
    )

    # Give the learner different starting mastery levels.
    initial_mastery = {
        "code-tracing": 0.80,
        "conditionals": 0.15,
        "loops": 0.60,
    }

    for skill_id, probability in initial_mastery.items():
        create_mastery(
            learner.id,
            skill_id,
            probability,
            db_path,
        )

    # Find task-002, which tests code tracing and conditionals.
    tasks = get_all_tasks(db_path)
    task = next(task for task in tasks if task.id == "task-002")

    # Act: the learner answers incorrectly.
    attempt = Attempt(
        id="attempt-001",
        learner_id=learner.id,
        task_id=task.id,
        submitted_answer="small",
        is_correct=False,
        hints_used=0,
        duration_seconds=30.0,
    )

    record_attempt(attempt, db_path)

    updated_mastery = update_learner_mastery(
        attempt,
        task.skill_ids,
        db_path,
    )

    # Assert: the incorrect answer reduced mastery.
    conditionals_mastery = get_mastery(
        learner.id,
        "conditionals",
        db_path,
    )

    code_tracing_mastery = get_mastery(
        learner.id,
        "code-tracing",
        db_path,
    )

    assert conditionals_mastery.probability_known < initial_mastery["conditionals"]
    assert code_tracing_mastery.probability_known < initial_mastery["code-tracing"]

    # The learner's weakest skill should still be conditionals.
    assert conditionals_mastery.probability_known < code_tracing_mastery.probability_known

    # Ask the adaptive selector for the next task.
    next_task = select_next_task(learner.id, db_path)

    # task-002 has been attempted, so task-005 is the easiest
    # remaining task targeting the learner's weakest skill.
    assert next_task is not None
    assert next_task.id == "task-005"
    assert "conditionals" in next_task.skill_ids



def test_selector_changes_skill_after_learner_improves(tmp_path):
    db_path = tmp_path / "test_recovery.db"
    seed_database(db_path)

    learner = create_learner(
        "Recovery learner",
        db_path=db_path,
        learner_id="recovery-learner",
    )

    initial_mastery = {
        "code-tracing": 0.80,
        "conditionals": 0.15,
        "loops": 0.60,
    }

    for skill_id, probability in initial_mastery.items():
        create_mastery(
            learner.id,
            skill_id,
            probability,
            db_path,
        )

    tasks = get_all_tasks(db_path)

    def submit_attempt(task_id, is_correct, answer, attempt_id):
        task = next(task for task in tasks if task.id == task_id)

        attempt = Attempt(
            id=attempt_id,
            learner_id=learner.id,
            task_id=task.id,
            submitted_answer=answer,
            is_correct=is_correct,
            hints_used=0,
            duration_seconds=30.0,
        )

        record_attempt(attempt, db_path)

        update_learner_mastery(
            attempt,
            task.skill_ids,
            db_path,
        )

    # First, the learner struggles with conditionals.
    submit_attempt(
        "task-002",
        False,
        "small",
        "attempt-001",
    )

    next_task = select_next_task(learner.id, db_path)
    assert next_task.id == "task-005"

    # The learner then answers two conditional questions correctly.
    submit_attempt(
        "task-005",
        True,
        "Allowed",
        "attempt-002",
    )

    submit_attempt(
        "task-006",
        True,
        "A",
        "attempt-003",
    )

    # Conditional mastery should now exceed loop mastery.
    conditional_mastery = get_mastery(
        learner.id,
        "conditionals",
        db_path,
    )

    loop_mastery = get_mastery(
        learner.id,
        "loops",
        db_path,
    )

    assert (
        conditional_mastery.probability_known
        > loop_mastery.probability_known
    )

    # The selector should now prioritise loops.
    next_task = select_next_task(learner.id, db_path)

    assert next_task is not None
    assert next_task.id == "task-003"
    assert "loops" in next_task.skill_ids
