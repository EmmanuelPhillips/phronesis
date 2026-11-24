from phronesis.models import Task


SUPPORTED_TASK_TYPES = {
    "predict_output",
    "short_answer",
}

MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 3


def validate_generated_task(
    task: Task,
    valid_skill_ids: set[str],
    existing_task_ids: set[str] | None = None,
) -> None:
    """
    Validate an LLM-generated task before it is stored.

    Raises ValueError if the task violates application rules.
    Returns None if validation succeeds.
    """

    if existing_task_ids is None:
        existing_task_ids = set()

    # Check task identity.
    if not task.id or not task.id.strip():
        raise ValueError("Task ID cannot be empty.")

    if task.id in existing_task_ids:
        raise ValueError(f"Task ID already exists: {task.id}")

    # Check descriptive fields.
    if not task.title or not task.title.strip():
        raise ValueError("Task title cannot be empty.")

    if not task.description or not task.description.strip():
        raise ValueError("Task description cannot be empty.")

    if not task.expected_answer or not task.expected_answer.strip():
        raise ValueError("Expected answer cannot be empty.")

    # Check task type.
    if task.task_type not in SUPPORTED_TASK_TYPES:
        raise ValueError(f"Unsupported task type: {task.task_type}")

    # Check difficulty.
    if (
        isinstance(task.difficulty, bool)
        or not isinstance(task.difficulty, int)
        or not MIN_DIFFICULTY <= task.difficulty <= MAX_DIFFICULTY
    ):
        raise ValueError(
            f"Difficulty must be an integer between "
            f"{MIN_DIFFICULTY} and {MAX_DIFFICULTY}."
        )

    # Predict-output tasks require a code sample.
    if task.task_type == "predict_output":
        if not task.code or not task.code.strip():
            raise ValueError("Predict-output tasks require code.")

    # Check associated skills.
    if not task.skill_ids:
        raise ValueError("A task must reference at least one skill.")

    if len(task.skill_ids) != len(set(task.skill_ids)):
        raise ValueError("A task cannot contain duplicate skill IDs.")

    unknown_skills = set(task.skill_ids) - valid_skill_ids

    if unknown_skills:
        raise ValueError(
            f"Task references unknown skills: {sorted(unknown_skills)}"
        )

    # Check hints.
    if not task.hints:
        raise ValueError("A task must contain at least one hint.")

    if any(not isinstance(hint, str) or not hint.strip() for hint in task.hints):
        raise ValueError("Hints must be non-empty strings.")
