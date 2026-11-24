import subprocess

import pytest

from phronesis.models import Task
from phronesis.task_verification import verify_task
import phronesis.task_verification as verification


def make_task(code, expected_answer):
    return Task(
        id="test-task",
        title="Test task",
        description="Predict the output.",
        code=code,
        task_type="predict_output",
        difficulty=1,
        expected_answer=expected_answer,
        skill_ids=["code-tracing"],
        hints=["Trace the code."],
    )


def test_correct_output_passes_verification():
    task = make_task(
        "print(2 + 2)",
        "4",
    )

    result = verify_task(task)

    assert result.is_valid is True
    assert result.actual_output.strip() == "4"
    assert result.error is None


def test_incorrect_expected_output_fails_verification():
    task = make_task(
        "print(2 + 2)",
        "5",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert result.actual_output.strip() == "4"
    assert result.error == "Expected output did not match actual output."


def test_multiline_output_passes_verification():
    task = make_task(
        "for i in range(1, 4):\n    print(i)",
        "1\n2\n3",
    )

    result = verify_task(task)

    assert result.is_valid is True


def test_nested_loop_output_passes_verification():
    task = make_task(
        "for i in range(1, 3):\n"
        "    for j in range(1, 3):\n"
        "        print(i * j, end=' ')\n"
        "    print()",
        "1 2\n2 4",
    )

    result = verify_task(task)

    assert result.is_valid is True


def test_invalid_syntax_is_rejected():
    task = make_task(
        "for i in range(:\n    print(i)",
        "1",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert "invalid syntax" in result.error


def test_import_statements_are_rejected():
    task = make_task(
        "import os\nprint(1)",
        "1",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert "Unsupported Python syntax" in result.error


def test_arbitrary_function_calls_are_rejected():
    task = make_task(
        "open('test.txt')",
        "",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert "Function not permitted" in result.error


def test_while_loops_are_rejected():
    task = make_task(
        "while True:\n    print('hello')",
        "hello",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert "Unsupported Python syntax" in result.error


def test_excessive_loop_iterations_are_rejected():
    task = make_task(
        "for i in range(100001):\n    print(i)",
        "",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert "Iteration limit exceeded" in result.error


def test_excessive_output_is_rejected():
    task = make_task(
        "for i in range(1000):\n"
        "    print('x' * 100)",
        "",
    )

    result = verify_task(task)

    assert result.is_valid is False
    assert "output limit" in result.error


def test_execution_timeout_is_handled(monkeypatch):
    task = make_task(
        "print(1)",
        "1",
    )

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd="python",
            timeout=0.01,
        )

    monkeypatch.setattr(
        verification.subprocess,
        "run",
        fake_run,
    )

    result = verify_task(task, timeout_seconds=0.01)

    assert result.is_valid is False
    assert "time limit" in result.error


def test_unsupported_task_type_is_rejected():
    task = make_task(
        "print(1)",
        "1",
    )
    task.task_type = "short_answer"

    with pytest.raises(ValueError, match="Cannot verify task type"):
        verify_task(task)
