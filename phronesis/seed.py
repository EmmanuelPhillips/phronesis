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
    Task(
        id="task-004",
        title="Variable reassignment",
        description="What does this code print?",
        code="x = 4\ny = x * 2\nx = y + 3\nprint(x)",
        task_type="predict_output",
        difficulty=2,
        expected_answer="11",
        skill_ids=["code-tracing"],
        hints=[
            "Track the values of x and y separately.",
            "What is y after the multiplication?",
        ],
    ),
    Task(
        id="task-005",
        title="Combining conditions",
        description="What does this code print?",
        code=(
            "age = 20\n"
            "has_ticket = True\n"
            "if age >= 18 and has_ticket:\n"
            "    print('Allowed')\n"
            "else:\n"
            "    print('Denied')"
        ),
        task_type="predict_output",
        difficulty=2,
        expected_answer="Allowed",
        skill_ids=["code-tracing", "conditionals"],
        hints=[
            "The and operator requires both conditions to be true.",
            "Check the age and has_ticket values.",
        ],
    ),
    Task(
        id="task-006",
        title="Nested conditionals",
        description="What does this code print?",
        code=(
            "x = 8\n"
            "if x > 5:\n"
            "    if x < 10:\n"
            "        print('A')\n"
            "    else:\n"
            "        print('B')\n"
            "else:\n"
            "    print('C')"
        ),
        task_type="predict_output",
        difficulty=3,
        expected_answer="A",
        skill_ids=["code-tracing", "conditionals"],
        hints=[
            "Start with the outer condition.",
            "Both conditions must be satisfied to print A.",
        ],
    ),
    Task(
        id="task-007",
        title="Accumulating values",
        description="What does this code print?",
        code=(
            "total = 0\n"
            "for i in range(1, 4):\n"
            "    total += i\n"
            "print(total)"
        ),
        task_type="predict_output",
        difficulty=2,
        expected_answer="6",
        skill_ids=["code-tracing", "loops"],
        hints=[
            "range(1, 4) starts at 1 and stops before 4.",
            "Track total after every iteration.",
        ],
    ),
    Task(
        id="task-008",
        title="Nested loops",
        description="What does this code print?",
        code=(
            "for i in range(2):\n"
            "    for j in range(2):\n"
            "        print(i + j)"
        ),
        task_type="predict_output",
        difficulty=3,
        expected_answer="0\n1\n1\n2",
        skill_ids=["code-tracing", "loops"],
        hints=[
            "The inner loop completes twice for each outer iteration.",
            "Calculate i + j for each pair of values.",
        ],
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
