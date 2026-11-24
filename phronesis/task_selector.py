from pathlib import Path

from phronesis.database import DATABASE_PATH
from phronesis.models import Task
from phronesis.repository import (
    get_all_tasks,
    get_learner_attempts,
    get_mastery,
)


def select_next_task(
    learner_id: str,
    db_path: Path = DATABASE_PATH,
) -> Task | None:
    """Select a task targeting the learner's weakest skill."""

    tasks = get_all_tasks(db_path)

    if not tasks:
        return None

    attempts = get_learner_attempts(learner_id, db_path)

    completed_task_ids = {
        attempt.task_id for attempt in attempts
    }

    # Collect all skills represented by available tasks.
    skill_ids = sorted({
        skill_id
        for task in tasks
        for skill_id in task.skill_ids
    })

    if not skill_ids:
        return None

    # Retrieve mastery estimates for each skill.
    mastery_levels = {}

    for skill_id in skill_ids:
        mastery = get_mastery(
            learner_id,
            skill_id,
            db_path,
        )

        mastery_levels[skill_id] = (
            mastery.probability_known if mastery
            else 0.20
        )

    # Find the weakest skill.
    # Alphabetical ordering provides deterministic tie-breaking.
    weakest_skill = min(
        skill_ids,
        key=lambda skill_id: (
            mastery_levels[skill_id],
            skill_id,
        ),
    )

    # Find tasks associated with the weakest skill.
    matching_tasks = [
        task for task in tasks
        if weakest_skill in task.skill_ids
    ]

    # Prefer tasks that haven't been attempted.
    uncompleted_tasks = [
        task for task in matching_tasks
        if task.id not in completed_task_ids
    ]

    if uncompleted_tasks:
        matching_tasks = uncompleted_tasks

    # Select the easiest available matching task.
    return min(
        matching_tasks,
        key=lambda task: (task.difficulty, task.id),
    )
