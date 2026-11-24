import pytest

from phronesis.models import Task
from phronesis.task_validation import validate_generated_task


VALID_SKILLS = {"code-tracing", "conditionals", "loops"}


def make_task(**overrides):
    values = {
        "id": "generated-001",
        "title": "Predict the output",
        "description": "What does this code print?",
        "code": "print(2 + 2)",
        "task_type": "predict_output",
        "difficulty": 1,
        "expected_answer": "4",
        "skill_ids": ["code-tracing"],
        "hints": ["Evaluate the expression."],
    }

    values.update(overrides)

    return Task(**values)


def test_valid_generated_task_passes():
    task = make_task()

    validate_generated_task(task, VALID_SKILLS)


def test_duplicate_task_id_is_rejected():
    task = make_task()

    with pytest.raises(ValueError, match="already exists"):
        validate_generated_task(
            task,
            VALID_SKILLS,
            existing_task_ids={"generated-001"},
        )


def test_empty_title_is_rejected():
    task = make_task(title="")

    with pytest.raises(ValueError, match="title"):
        validate_generated_task(task, VALID_SKILLS)


def test_unsupported_task_type_is_rejected():
    task = make_task(task_type="write_code")

    with pytest.raises(ValueError, match="Unsupported task type"):
        validate_generated_task(task, VALID_SKILLS)


def test_invalid_difficulty_is_rejected():
    task = make_task(difficulty=5)

    with pytest.raises(ValueError, match="Difficulty"):
        validate_generated_task(task, VALID_SKILLS)


def test_unknown_skill_is_rejected():
    task = make_task(skill_ids=["nonexistent-skill"])

    with pytest.raises(ValueError, match="unknown skills"):
        validate_generated_task(task, VALID_SKILLS)


def test_task_without_skills_is_rejected():
    task = make_task(skill_ids=[])

    with pytest.raises(ValueError, match="at least one skill"):
        validate_generated_task(task, VALID_SKILLS)


def test_duplicate_skills_are_rejected():
    task = make_task(
        skill_ids=["loops", "loops"]
    )

    with pytest.raises(ValueError, match="duplicate skill"):
        validate_generated_task(task, VALID_SKILLS)


def test_predict_output_without_code_is_rejected():
    task = make_task(code="")

    with pytest.raises(ValueError, match="require code"):
        validate_generated_task(task, VALID_SKILLS)


def test_empty_expected_answer_is_rejected():
    task = make_task(expected_answer="")

    with pytest.raises(ValueError, match="Expected answer"):
        validate_generated_task(task, VALID_SKILLS)


def test_task_without_hints_is_rejected():
    task = make_task(hints=[])

    with pytest.raises(ValueError, match="at least one hint"):
        validate_generated_task(task, VALID_SKILLS)
