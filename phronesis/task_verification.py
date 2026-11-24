import ast
import subprocess
import tempfile
from dataclasses import dataclass
import sys

from phronesis.evaluation import normalize_output
from phronesis.models import Task


MAX_CODE_LENGTH = 10_000
MAX_OUTPUT_BYTES = 65_536
MAX_TOTAL_ITERATIONS = 100_000
DEFAULT_TIMEOUT = 2.0


@dataclass
class TaskVerificationResult:
    is_valid: bool
    actual_output: str
    expected_output: str
    error: str | None = None


ALLOWED_NODES = (
    ast.Module,
    ast.Expr,
    ast.Assign,
    ast.AugAssign,
    ast.For,
    ast.If,
    ast.Name,
    ast.Constant,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.BoolOp,
    ast.Call,
    ast.keyword,
    ast.Load,
    ast.Store,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.And,
    ast.Or,
)


def validate_python_code(code: str) -> None:
    """Check that generated code only uses supported Python syntax."""

    if not code or not code.strip():
        raise ValueError("Generated code cannot be empty.")

    if len(code) > MAX_CODE_LENGTH:
        raise ValueError("Generated code exceeds the size limit.")

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        raise ValueError(
            f"Generated code has invalid syntax: {error}"
        ) from error

    for node in ast.walk(tree):

        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(
                f"Unsupported Python syntax: {type(node).__name__}"
            )

        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                if node.id in {"print", "range"}:
                    raise ValueError(
                        f"Cannot overwrite built-in name: {node.id}"
                    )

        if isinstance(node, ast.For):
            if not isinstance(node.target, ast.Name):
                raise ValueError(
                    "For loops must use a single variable."
                )

            if not (
                isinstance(node.iter, ast.Call)
                and isinstance(node.iter.func, ast.Name)
                and node.iter.func.id == "range"
            ):
                raise ValueError(
                    "For loops must iterate over range()."
                )

        if isinstance(node, ast.Call):

            if not isinstance(node.func, ast.Name):
                raise ValueError(
                    "Only direct function calls are supported."
                )

            if node.func.id not in {"print", "range"}:
                raise ValueError(
                    f"Function not permitted: {node.func.id}"
                )

            if node.func.id == "range":
                if node.keywords or not 1 <= len(node.args) <= 3:
                    raise ValueError(
                        "range() must have between one and three "
                        "positional arguments."
                    )

            if node.func.id == "print":
                for keyword in node.keywords:
                    if keyword.arg not in {"end", "sep"}:
                        raise ValueError(
                            "Only end and sep are permitted "
                            "as print() keyword arguments."
                        )

                    if not (
                        isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        raise ValueError(
                            "print() end and sep must be strings."
                        )

        if isinstance(node, ast.Constant):
            if not isinstance(
                node.value,
                (int, float, bool, str, type(None)),
            ):
                raise ValueError(
                    "Unsupported constant type."
                )


WORKER_CODE = """
import resource
import sys

MAX_TOTAL_ITERATIONS = 100_000
iteration_count = 0

# Limit CPU time and the maximum size of output files.
resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
resource.setrlimit(
    resource.RLIMIT_FSIZE,
    (65_536, 65_536),
)


def safe_range(*args):
    global iteration_count

    values = range(*args)

    try:
        count = len(values)
    except OverflowError as error:
        raise RuntimeError("Loop is too large.") from error

    iteration_count += count

    if iteration_count > MAX_TOTAL_ITERATIONS:
        raise RuntimeError("Iteration limit exceeded.")

    return values


source = sys.stdin.read()

namespace = {
    "__builtins__": {},
    "print": print,
    "range": safe_range,
}

exec(compile(source, "<generated-task>", "exec"), namespace)
"""


def verify_task(
    task: Task,
    timeout_seconds: float = DEFAULT_TIMEOUT,
) -> TaskVerificationResult:
    """Execute a validated task and compare its output."""

    if task.task_type != "predict_output":
        raise ValueError(
            f"Cannot verify task type: {task.task_type}"
        )

    try:
        validate_python_code(task.code)
    except ValueError as error:
        return TaskVerificationResult(
            is_valid=False,
            actual_output="",
            expected_output=task.expected_answer,
            error=str(error),
        )

    with tempfile.TemporaryFile() as stdout_file, \
            tempfile.TemporaryFile() as stderr_file:

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-S",
                    "-c",
                    WORKER_CODE,
                ],
                input=task.code,
                text=True,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=timeout_seconds,
                check=False,
            )

        except subprocess.TimeoutExpired:
            return TaskVerificationResult(
                is_valid=False,
                actual_output="",
                expected_output=task.expected_answer,
                error="Code execution exceeded the time limit.",
            )

        stdout_file.seek(0)
        actual_output = stdout_file.read().decode(
            "utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            stderr_file.seek(0)
            error_output = stderr_file.read().decode(
                "utf-8",
                errors="replace",
            )

            if len(actual_output) >= MAX_OUTPUT_BYTES:
                error_message = "Generated code exceeded the output limit."
            else:
                error_message = (
                    error_output.strip()[:500]
                    or "Generated code failed during execution."
                )

            return TaskVerificationResult(
                is_valid=False,
                actual_output=actual_output,
                expected_output=task.expected_answer,
                error=error_message,
            )

    matches = (
        normalize_output(actual_output)
        == normalize_output(task.expected_answer)
    )

    return TaskVerificationResult(
        is_valid=matches,
        actual_output=actual_output,
        expected_output=task.expected_answer,
        error=None if matches else "Expected output did not match actual output.",
    )
