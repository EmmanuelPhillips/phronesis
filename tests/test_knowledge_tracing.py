import pytest

from phronesis.knowledge_tracing import (
    BKTParameters,
    update_mastery,
)


@pytest.fixture
def parameters():
    return BKTParameters()


def test_correct_answer_increases_mastery(parameters):
    initial_mastery = 0.20

    updated_mastery = update_mastery(
        initial_mastery,
        True,
        parameters,
    )

    assert updated_mastery > initial_mastery


def test_incorrect_answer_decreases_mastery(parameters):
    initial_mastery = 0.20

    updated_mastery = update_mastery(
        initial_mastery,
        False,
        parameters,
    )

    assert updated_mastery < initial_mastery


def test_repeated_correct_answers_increase_mastery(parameters):
    mastery = 0.20

    for _ in range(5):
        mastery = update_mastery(mastery, True, parameters)

    assert mastery > 0.80


def test_mastery_remains_within_valid_probability_range(parameters):
    mastery = 0.20

    for _ in range(20):
        mastery = update_mastery(mastery, True, parameters)

    assert 0.0 <= mastery <= 1.0


def test_correct_answer_produces_expected_mastery(parameters):
    initial_mastery = 0.20

    updated_mastery = update_mastery(
        initial_mastery,
        True,
        parameters,
    )

    assert updated_mastery == pytest.approx(0.5764705882)
