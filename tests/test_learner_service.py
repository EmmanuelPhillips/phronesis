import pytest

from phronesis.database import initialize_database
from phronesis.learner_service import update_learner_mastery
from phronesis.models import Attempt, Skill
from phronesis.repository import (
    create_learner,
    create_skill,
    get_mastery,
)


@pytest.fixture
def setup_database(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    learner = create_learner("Test learner", db_path)

    skills = [
        Skill("loops", "Loops", "Understanding iteration"),
        Skill("conditionals", "Conditionals", "Understanding conditions"),
    ]

    for skill in skills:
        create_skill(skill, db_path)

    return db_path, learner


def make_attempt(learner_id, is_correct):
    return Attempt(
        id="attempt-001",
        learner_id=learner_id,
        task_id="task-001",
        submitted_answer="8",
        is_correct=is_correct,
        hints_used=0,
        duration_seconds=15.0,
    )


def test_first_attempt_creates_initial_mastery(setup_database):
    db_path, learner = setup_database

    attempt = make_attempt(learner.id, True)

    update_learner_mastery(
        attempt,
        ["loops"],
        db_path,
    )

    mastery = get_mastery(learner.id, "loops", db_path)

    assert mastery is not None
    assert mastery.probability_known == pytest.approx(0.5764705882)


def test_correct_attempt_increases_existing_mastery(setup_database):
    db_path, learner = setup_database

    first_attempt = make_attempt(learner.id, True)

    update_learner_mastery(
        first_attempt,
        ["loops"],
        db_path,
    )

    previous_mastery = get_mastery(
        learner.id,
        "loops",
        db_path,
    ).probability_known

    second_attempt = make_attempt(learner.id, True)

    update_learner_mastery(
        second_attempt,
        ["loops"],
        db_path,
    )

    new_mastery = get_mastery(
        learner.id,
        "loops",
        db_path,
    ).probability_known

    assert new_mastery > previous_mastery


def test_incorrect_attempt_decreases_existing_mastery(setup_database):
    db_path, learner = setup_database

    first_attempt = make_attempt(learner.id, True)

    update_learner_mastery(
        first_attempt,
        ["loops"],
        db_path,
    )

    previous_mastery = get_mastery(
        learner.id,
        "loops",
        db_path,
    ).probability_known

    second_attempt = make_attempt(learner.id, False)

    update_learner_mastery(
        second_attempt,
        ["loops"],
        db_path,
    )

    new_mastery = get_mastery(
        learner.id,
        "loops",
        db_path,
    ).probability_known

    assert new_mastery < previous_mastery


def test_multiple_skills_are_updated(setup_database):
    db_path, learner = setup_database

    attempt = make_attempt(learner.id, True)

    updated = update_learner_mastery(
        attempt,
        ["loops", "conditionals"],
        db_path,
    )

    assert len(updated) == 2

    for skill in updated:
        assert skill.probability_known == pytest.approx(
            0.5764705882
        )
