import pytest

from phronesis.database import initialize_database
from phronesis.models import Skill, Task
from phronesis.repository import (
    create_learner,
    create_mastery,
    create_skill,
    create_task,
    get_all_tasks,
    get_mastery,
    update_mastery_record,
)


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    initialize_database(path)
    return path


@pytest.fixture
def loops_skill(db_path):
    skill = Skill(
        id="loops",
        name="Loops",
        description="Understanding iteration",
    )
    create_skill(skill, db_path)
    return skill


def _setup_learner_and_skill(db_path, skill):
    learner = create_learner("Test learner", db_path)
    return learner, skill


def test_create_and_get_mastery(db_path, loops_skill):
    learner, skill = _setup_learner_and_skill(db_path, loops_skill)

    created = create_mastery(learner.id, skill.id, 0.20, db_path)
    retrieved = get_mastery(learner.id, skill.id, db_path)

    assert created.probability_known == 0.20
    assert retrieved == created


def test_get_mastery_returns_none_when_missing(db_path):
    assert get_mastery("missing", "missing", db_path) is None


def test_update_mastery_record(db_path, loops_skill):
    learner, skill = _setup_learner_and_skill(db_path, loops_skill)
    target_prob = 0.5764705882

    create_mastery(learner.id, skill.id, 0.20, db_path)
    updated = update_mastery_record(learner.id, skill.id, target_prob, db_path)
    retrieved = get_mastery(learner.id, skill.id, db_path)

    assert updated.probability_known == pytest.approx(target_prob)
    assert retrieved.probability_known == pytest.approx(target_prob)


def test_create_mastery_rejects_invalid_probability(db_path, loops_skill):
    learner, skill = _setup_learner_and_skill(db_path, loops_skill)

    with pytest.raises(ValueError):
        create_mastery(learner.id, skill.id, 1.5, db_path)


def test_create_and_retrieve_task(db_path, loops_skill):
    task = Task(
        id="task-001",
        title="Predict output",
        description="What does the code print?",
        code="print(2 + 2)",
        task_type="predict_output",
        difficulty=1,
        expected_answer="4",
        skill_ids=[loops_skill.id],
        hints=["Add the two numbers."],
    )

    create_task(task, db_path)
    retrieved_tasks = get_all_tasks(db_path)

    assert len(retrieved_tasks) == 1
    assert retrieved_tasks[0].title == "Predict output"
    assert retrieved_tasks[0].skill_ids == [loops_skill.id]
    assert retrieved_tasks[0].hints == ["Add the two numbers."]
