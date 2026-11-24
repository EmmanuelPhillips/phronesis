from dataclasses import dataclass

from phronesis.models import Task


@dataclass
class EvaluationResult:
    is_correct: bool
    feedback: str
    expected_answer: str


def normalize_output(answer: str) -> str:
    """Normalize output while preserving meaningful line breaks."""

    return "\n".join(
        line.rstrip()
        for line in answer.strip().replace("\r\n", "\n").splitlines()
    )


def normalize_short_answer(answer: str) -> str:
    """Normalize a written answer for comparison."""

    return " ".join(answer.casefold().split())


def evaluate_output_prediction(
    submitted_answer: str,
    expected_answer: str,
) -> EvaluationResult:
    """Evaluate a predicted program output."""

    is_correct = (
        normalize_output(submitted_answer)
        == normalize_output(expected_answer)
    )

    feedback = (
        "Correct! Your predicted output matches."
        if is_correct
        else "Not quite. Your predicted output does not match."
    )

    return EvaluationResult(
        is_correct=is_correct,
        feedback=feedback,
        expected_answer=expected_answer,
    )


def evaluate_short_answer(
    submitted_answer: str,
    expected_answer: str,
) -> EvaluationResult:
    """Evaluate a short written answer."""

    is_correct = (
        normalize_short_answer(submitted_answer)
        == normalize_short_answer(expected_answer)
    )

    feedback = (
        "Correct! Your answer matches."
        if is_correct
        else "Not quite. Try reviewing the concept."
    )

    return EvaluationResult(
        is_correct=is_correct,
        feedback=feedback,
        expected_answer=expected_answer,
    )

def evaluate_task(task: Task, submitted_answer: str) -> EvaluationResult:
    if task.task_type in ("output", "predict_output"):
        return evaluate_output_prediction(
            submitted_answer,
            task.expected_answer
        )

    if task.task_type == "short_answer":
        return evaluate_short_answer(
            submitted_answer,
            task.expected_answer
        )

    raise ValueError(f"Unsupported task type: {task.task_type}")
