import json
from types import SimpleNamespace

import pytest

from phronesis.llm_generator import (
    OllamaTaskGenerator,
    TASK_SCHEMA,
)


VALID_SKILLS = {"code-tracing", "conditionals", "loops"}


def make_response(count=1):
    tasks = []

    for i in range(count):
        tasks.append({
            "title": f"Generated question {i}",
            "description": "What does this code print?",
            "code": "print(2 + 2)",
            "task_type": "predict_output",
            "difficulty": 1,
            "expected_answer": "4",
            "skill_ids": ["code-tracing"],
            "hints": ["Evaluate the expression."],
        })

    return json.dumps({"tasks": tasks})


class FakeClient:
    def __init__(self, output_text):
        self.output_text = output_text
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)

        return SimpleNamespace(
            message=SimpleNamespace(
                content=self.output_text
            )
        )


def test_generates_and_parses_tasks():
    client = FakeClient(make_response())
    generator = OllamaTaskGenerator(client=client, model="test-model")

    tasks = generator.generate_tasks(
        topic="Python arithmetic",
        skill_ids=["code-tracing"],
        valid_skill_ids=VALID_SKILLS,
        difficulty=1,
        count=1,
    )

    assert len(tasks) == 1
    assert tasks[0].expected_answer == "4"
    assert tasks[0].task_type == "predict_output"


def test_uses_structured_output_schema():
    client = FakeClient(make_response())
    generator = OllamaTaskGenerator(client=client, model="test-model")

    generator.generate_tasks(
        topic="Python arithmetic",
        skill_ids=["code-tracing"],
        valid_skill_ids=VALID_SKILLS,
        difficulty=1,
        count=1,
    )

    call = client.calls[0]

    assert call["model"] == "test-model"
    assert call["format"] == TASK_SCHEMA


def test_empty_topic_is_rejected():
    generator = OllamaTaskGenerator(client=FakeClient(make_response()))

    with pytest.raises(ValueError, match="Topic"):
        generator.generate_tasks(
            topic="",
            skill_ids=["code-tracing"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=1,
        )


def test_unknown_skill_is_rejected():
    generator = OllamaTaskGenerator(client=FakeClient(make_response()))

    with pytest.raises(ValueError, match="Unknown skill"):
        generator.generate_tasks(
            topic="Python",
            skill_ids=["unknown"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=1,
        )


def test_invalid_difficulty_is_rejected():
    generator = OllamaTaskGenerator(client=FakeClient(make_response()))

    with pytest.raises(ValueError, match="Difficulty"):
        generator.generate_tasks(
            topic="Python",
            skill_ids=["code-tracing"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=5,
        )


def test_invalid_count_is_rejected():
    generator = OllamaTaskGenerator(client=FakeClient(make_response()))

    with pytest.raises(ValueError, match="Count"):
        generator.generate_tasks(
            topic="Python",
            skill_ids=["code-tracing"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=1,
            count=20,
        )


def test_empty_llm_response_is_rejected():
    generator = OllamaTaskGenerator(client=FakeClient(""))

    with pytest.raises(ValueError, match="empty response"):
        generator.generate_tasks(
            topic="Python",
            skill_ids=["code-tracing"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=1,
        )


def test_invalid_generated_task_is_rejected():
    invalid_response = make_response().replace(
        "code-tracing",
        "unknown-skill",
    )

    generator = OllamaTaskGenerator(
        client=FakeClient(invalid_response)
    )

    with pytest.raises(ValueError, match="unknown skills"):
        generator.generate_tasks(
            topic="Python",
            skill_ids=["code-tracing"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=1,
        )


def test_wrong_number_of_tasks_is_rejected():
    generator = OllamaTaskGenerator(
        client=FakeClient(make_response(count=1))
    )

    with pytest.raises(ValueError, match="Expected 2 tasks"):
        generator.generate_tasks(
            topic="Python",
            skill_ids=["code-tracing"],
            valid_skill_ids=VALID_SKILLS,
            difficulty=1,
            count=2,
        )
