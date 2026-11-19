from phronesis.models import Skill, Task, Learner, Attempt, Mastery


def test_skill_creation():
    skill = Skill(
        id="loops",
        name="Loops",
        description="Understanding iteration."
    )

    assert skill.id == "loops"
    assert skill.name == "Loops"


def test_task_creation():
    task = Task(
        id="task-1",
        title="Predict the output",
        description="Determine what the code prints.",
        code="print(2 + 2)",
        task_type="predict_output",
        difficulty=1,
        expected_answer="4",
        skill_ids=["arithmetic"],
        hints=["Evaluate the expression."]
    )

    assert task.expected_answer == "4"
    assert "arithmetic" in task.skill_ids


def test_learner_creation():
    learner = Learner(
        id="learner-1",
        name="Test Learner"
    )

    assert learner.name == "Test Learner"
    assert learner.created_at is not None


def test_mastery_creation():
    mastery = Mastery(
        learner_id="learner-1",
        skill_id="loops",
        probability_known=0.75
    )

    assert mastery.probability_known == 0.75
