import json

import pytest

from phronesis.task_generation import parse_generated_tasks


VALID_SKILLS = {"code-tracing", "conditionals", "loops"}


def make_response():
    return json.dumps({
        "tasks": [
            {
                "title": "Predict the output",
                "description": "What does this code print?",
                "code": "print(3 * 4)",
                "task_type": "predict_output",
                "difficulty": 1,
                "expected_answer": "12",
                "skill_ids": ["code-tracing"],
                "hints": ["Evaluate the multiplication."]
            }
        ]
    })


def test_parses_valid_generated_task():
    tasks = parse_generated_tasks(
        make_response(),
        VALID_SKILLS,
    )

    assert len(tasks) == 1
    assert tasks[0].title == "Predict the output"
    assert tasks[0].expected_answer == "12"
    assert tasks[0].task_type == "predict_output"


def test_generated_tasks_receive_unique_ids():
    response = json.dumps({
        "tasks": [
            {
                "title": f"Question {i}",
                "description": "Predict the output.",
                "code": "print(1)",
                "task_type": "predict_output",
                "difficulty": 1,
                "expected_answer": "1",
                "skill_ids": ["code-tracing"],
                "hints": ["Read the print statement."]
            }
            for i in range(2)
        ]
    })

    tasks = parse_generated_tasks(response, VALID_SKILLS)

    assert tasks[0].id != tasks[1].id


def test_invalid_json_is_rejected():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_generated_tasks(
            "This is not JSON",
            VALID_SKILLS,
        )


def test_missing_tasks_list_is_rejected():
    response = json.dumps({"questions": []})

    with pytest.raises(ValueError, match="tasks list"):
        parse_generated_tasks(response, VALID_SKILLS)


def test_empty_task_list_is_rejected():
    response = json.dumps({"tasks": []})

    with pytest.raises(ValueError, match="no tasks"):
        parse_generated_tasks(response, VALID_SKILLS)


def test_missing_task_fields_are_rejected():
    response = json.dumps({
        "tasks": [
            {
                "title": "Incomplete question",
                "description": "Missing several fields."
            }
        ]
    })

    with pytest.raises(ValueError, match="missing fields"):
        parse_generated_tasks(response, VALID_SKILLS)


def test_invalid_generated_task_is_rejected():
    response = json.dumps({
        "tasks": [
            {
                "title": "Invalid question",
                "description": "Unknown skill.",
                "code": "print(1)",
                "task_type": "predict_output",
                "difficulty": 1,
                "expected_answer": "1",
                "skill_ids": ["unknown-skill"],
                "hints": ["Read the code."]
            }
        ]
    })

    with pytest.raises(ValueError, match="unknown skills"):
        parse_generated_tasks(response, VALID_SKILLS)


def test_existing_task_ids_are_preserved():
    response = make_response()

    tasks = parse_generated_tasks(
        response,
        VALID_SKILLS,
        existing_task_ids={"task-001"},
    )

    assert tasks[0].id != "task-001"


def test_short_answer_task_can_have_empty_code():
    response = json.dumps({
        "tasks": [
            {
                "title": "What is a variable?",
                "description": "Explain what a variable represents.",
                "task_type": "short_answer",
                "difficulty": 1,
                "expected_answer": "A named storage location for a value.",
                "skill_ids": ["code-tracing"],
                "hints": ["Think about how values are stored."]
            }
        ]
    })

    tasks = parse_generated_tasks(response, VALID_SKILLS)

    assert tasks[0].task_type == "short_answer"
    assert tasks[0].code == ""
