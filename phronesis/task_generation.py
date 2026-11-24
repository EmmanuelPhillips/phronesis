import json
from uuid import uuid4

from phronesis.models import Task
from phronesis.task_validation import validate_generated_task


def parse_generated_tasks(
    response: str,
    valid_skill_ids: set[str],
    existing_task_ids: set[str] | None = None,
) -> list[Task]:
    """
    Parse an LLM JSON response into validated Task objects.

    Raises ValueError if the response is malformed or any
    generated task fails validation.
    """

    if existing_task_ids is None:
        existing_task_ids = set()

    try:
        payload = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError("LLM response is not valid JSON.") from error

    if not isinstance(payload, dict):
        raise ValueError("LLM response must contain a JSON object.")

    generated_tasks = payload.get("tasks")

    if not isinstance(generated_tasks, list):
        raise ValueError("LLM response must contain a tasks list.")

    if not generated_tasks:
        raise ValueError("LLM response contains no tasks.")

    tasks = []
    known_ids = set(existing_task_ids)

    for item in generated_tasks:
        if not isinstance(item, dict):
            raise ValueError("Each generated task must be a JSON object.")

        required_fields = {
            "title",
            "description",
            "task_type",
            "difficulty",
            "expected_answer",
            "skill_ids",
            "hints",
        }

        missing_fields = required_fields - item.keys()

        if missing_fields:
            raise ValueError(
                f"Generated task is missing fields: {sorted(missing_fields)}"
            )

        if "code" in item and not isinstance(item["code"], str):
            raise ValueError("Task code must be a string.")

        if not isinstance(item["skill_ids"], list):
            raise ValueError("Task skill_ids must be a list.")

        if not isinstance(item["hints"], list):
            raise ValueError("Task hints must be a list.")

        task = Task(
            id=f"generated-{uuid4().hex}",
            title=item["title"],
            description=item["description"],
            code=item.get("code", ""),
            task_type=item["task_type"],
            difficulty=item["difficulty"],
            expected_answer=item["expected_answer"],
            skill_ids=item["skill_ids"],
            hints=item["hints"],
        )

        validate_generated_task(
            task,
            valid_skill_ids,
            existing_task_ids=known_ids,
        )

        known_ids.add(task.id)
        tasks.append(task)

    return tasks
