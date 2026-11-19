from pathlib import Path

from phronesis.database import initialize_database
from phronesis.models import Skill, Task
from phronesis.repository import create_skill, create_task


SKILLS = [
    Skill(
        id="code-tracing",
        name="Code tracing",
        description="Following code execution and predicting its output.",
    ),
    Skill(
        id="conditionals",
        name="Conditionals",
        description="Understanding conditional statements and branching.",
    ),
    Skill(
        id="loops",
        name="Loops",
        description="Understanding iteration and repeated execution.",
    ),
]


TASKS = [
    Task(
        id="task-001",
        title="Predict the output",
        description="What does this code print?",
        code="x = 5\nx += 3\nprint(x)",
        task_type="predict_output",
        difficulty=1,
        expected_answer="8",
        skill_ids=["code-tracing"],
        hints=["Follow the assignment to x.", "What is 5 plus 3?"],
    ),
    Task(
        id="task-002",
        title="Understand conditionals",
        description="What does this code print?",
        code="x = 10\nif x > 5:\n    print('large')\nelse:\n    print('small')",
        task_type="predict_output",
        difficulty=1,
        expected_answer="large",
        skill_ids=["code-tracing", "conditionals"],
        hints=["Evaluate the condition first.", "Is 10 greater than 5?"],
    ),
    Task(
        id="task-003",
        title="Trace a loop",
        description="What does this code print?",
        code="total = 0\nfor i in range(3):\n    total += i\nprint(total)",
        task_type="predict_output",
        difficulty=2,
        expected_answer="3",
        skill_ids=["code-tracing", "loops"],
        hints=["What values does range(3) produce?", "Add those values together."],
    ),
]


def seed_database(db_path: Path | None = None) -> None:
    if db_path is None:
        initialize_database()
    else:
        initialize_database(db_path)

    for skill in SKILLS:
        create_skill(skill, db_path) if db_path else create_skill(skill)

    for task in TASKS:
        create_task(task, db_path) if db_path else create_task(task)


if __name__ == "__main__":
    seed_database()
    print("Phronesis database seeded successfully.")
