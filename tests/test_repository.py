from phronesis.database import initialize_database
from phronesis.models import Skill, Task
from phronesis.repository import (
    create_skill,
    create_task,
    get_all_tasks,
)


def test_create_and_retrieve_task(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    skill = Skill(
        id="loops",
        name="Loops",
        description="Understanding iteration.",
    )

    task = Task(
        id="task-001",
        title="Predict output",
        description="What does the code print?",
        code="print(2 + 2)",
        task_type="predict_output",
        difficulty=1,
        expected_answer="4",
        skill_ids=["loops"],
        hints=["Add the two numbers."],
    )

    create_skill(skill, db_path)
    create_task(task, db_path)

    retrieved_tasks = get_all_tasks(db_path)

    assert len(retrieved_tasks) == 1
    assert retrieved_tasks[0].title == "Predict output"
    assert retrieved_tasks[0].skill_ids == ["loops"]
    assert retrieved_tasks[0].hints == ["Add the two numbers."]
