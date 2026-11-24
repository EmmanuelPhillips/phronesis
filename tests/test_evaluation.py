import pytest

from phronesis.evaluation import (
    evaluate_output_prediction,
    evaluate_short_answer,
    evaluate_task,
)
from phronesis.models import Task


def test_correct_output_prediction():
    result = evaluate_output_prediction("8", "8")

    assert result.is_correct is True


def test_incorrect_output_prediction():
    result = evaluate_output_prediction("9", "8")

    assert result.is_correct is False


def test_output_ignores_surrounding_whitespace():
    result = evaluate_output_prediction("  8\n", "8")

    assert result.is_correct is True


def test_output_preserves_line_breaks():
    result = evaluate_output_prediction(
        "1\n2\n3",
        "1\n3\n2",
    )

    assert result.is_correct is False


def test_correct_short_answer_ignores_capitalisation():
    result = evaluate_short_answer(
        "PYTHON LOOPS",
        "Python loops",
    )

    assert result.is_correct is True


def test_short_answer_ignores_extra_whitespace():
    result = evaluate_short_answer(
        "  Python    loops  ",
        "Python loops",
    )

    assert result.is_correct is True


def test_evaluate_task_dispatches_output_task():
    task = Task(
        id="task-001",
        title="Output prediction",
        description="Predict the output",
        code="print(5 + 3)",
        task_type="output",
        difficulty=1,
        expected_answer="8",
        skill_ids=["code-tracing"],
    )

    result = evaluate_task(task, "8")

    assert result.is_correct is True


def test_evaluate_task_dispatches_short_answer_task():
    task = Task(
        id="task-002",
        title="Explain loops",
        description="Explain what a loop does",
        code="",
        task_type="short_answer",
        difficulty=1,
        expected_answer="repeated execution",
        skill_ids=["loops"],
    )

    result = evaluate_task(task, "Repeated execution")

    assert result.is_correct is True


def test_unsupported_task_type_raises_error():
    task = Task(
        id="task-003",
        title="Code submission",
        description="Write a function",
        code="",
        task_type="code",
        difficulty=2,
        expected_answer="",
        skill_ids=["code-tracing"],
    )

    with pytest.raises(ValueError, match="Unsupported task type"):
        evaluate_task(task, "def solution(): pass")

def test_evaluate_predict_output_task():
    task = Task(
        id="task-1",
        title="Predict output",
        description="Predict the output of this code.",
        code="print(2 + 2)",
        task_type="predict_output",
        difficulty=1,
        expected_answer="4",
        skill_ids=["python_basics"]
    )

    result = evaluate_task(task, "4")

    assert result.is_correct is True
